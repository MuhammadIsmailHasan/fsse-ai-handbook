"""Checks for redis_patterns.py against a real Redis. Don't edit this file.

Start Redis first:  cd exercises && docker compose up -d redis
"""

import os
import threading
import time
import uuid

import pytest
import redis

from redis_patterns import InProgressError, ReliableQueue, SlidingWindowRateLimiter, cache_aside, cache_with_lock, invalidate, run_once

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6391/15")


@pytest.fixture()
def r():
    client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    try:
        client.ping()
    except redis.ConnectionError:
        pytest.fail("Redis isn't running on port 6391 — run: cd exercises && docker compose up -d redis")
    prefix = f"t{uuid.uuid4().hex[:8]}"
    yield client, prefix
    keys = list(client.scan_iter(f"*{prefix}*"))
    if keys:
        client.delete(*keys)


class Clock:
    def __init__(self, now=1_000.0):
        self.now = now

    def __call__(self):
        return self.now


def test_cache_aside(r):
    client, p = r
    calls = []

    def loader():
        calls.append(1)
        return {"id": 7, "name": "Batik Shirt", "price": "150000.00", "tags": ["sale"]}

    key = f"{p}:product:7"
    assert cache_aside(client, key, 300, loader, rng=lambda: 0.5) == loader()
    calls.clear()
    assert cache_aside(client, key, 300, loader) == {"id": 7, "name": "Batik Shirt", "price": "150000.00", "tags": ["sale"]}
    assert calls == []
    assert client.ttl(key) in range(310, 316)  # 300 + int(300 * 0.1 * 0.5) = 315
    assert cache_aside(client, f"{p}:missing", 60, lambda: None) is None
    assert client.exists(f"{p}:missing") == 0
    assert invalidate(client, key, f"{p}:nope") == 1
    assert invalidate(client) == 0
    assert client.exists(key) == 0


def test_cache_with_lock_prevents_stampede(r):
    client, p = r
    key = f"{p}:bestsellers"
    calls = []
    barrier = threading.Barrier(20)

    def slow_loader():
        calls.append(1)
        time.sleep(0.3)
        return [1, 2, 3]

    results = []

    def worker():
        local = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        barrier.wait()
        results.append(cache_with_lock(local, key, 60, slow_loader))

    threads = [threading.Thread(target=worker) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(calls) == 1
    assert results == [[1, 2, 3]] * 20
    assert client.exists(f"lock:{key}") == 0
    assert 0 < client.ttl(key) <= 60


def test_cache_with_lock_releases_only_its_own_lock_and_times_out(r):
    client, p = r
    key = f"{p}:report"
    client.set(f"lock:{key}", "someone-else", px=10_000)
    started = time.monotonic()
    assert cache_with_lock(client, key, 60, lambda: {"fresh": True}, max_wait=0.3) == {"fresh": True}
    assert 0.25 < time.monotonic() - started < 2
    assert client.get(f"lock:{key}") == "someone-else"
    assert client.exists(key) == 0

    def expired_lock_loader():
        client.set(f"lock:{key}2", "new-owner", px=10_000)  # our lock expired and someone else took it
        return 42

    assert cache_with_lock(client, f"{key}2", 60, expired_lock_loader, lock_ttl_ms=1) == 42
    assert client.get(f"lock:{key}2") == "new-owner"


def test_rate_limiter_sliding_window(r):
    client, p = r
    clock = Clock()
    limiter = SlidingWindowRateLimiter(client, limit=3, window_seconds=10, prefix=f"{p}:rl", clock=clock)
    assert [limiter.allow("ip:1.2.3.4")[0] for _ in range(3)] == [True, True, True]
    assert limiter.allow("ip:1.2.3.4") == (False, 10.0)
    assert limiter.allow("ip:5.6.7.8") == (True, 0.0)
    clock.now += 4.5
    assert limiter.allow("ip:1.2.3.4") == (False, 5.5)
    assert client.zcard(f"{p}:rl:ip:1.2.3.4") == 3, "denied requests must not be recorded"
    clock.now += 5.6
    assert limiter.allow("ip:1.2.3.4") == (True, 0.0)
    assert 0 < client.ttl(f"{p}:rl:ip:1.2.3.4") <= 10


def test_rate_limiter_is_atomic_under_concurrency(r):
    client, p = r
    limiter_key = f"{p}:burst"
    allowed = []
    barrier = threading.Barrier(30)

    def hit():
        local = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        limiter = SlidingWindowRateLimiter(local, limit=5, window_seconds=60, prefix=limiter_key)
        barrier.wait()
        allowed.append(limiter.allow("login:sari@example.com")[0])

    threads = [threading.Thread(target=hit) for _ in range(30)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert allowed.count(True) == 5


def test_reliable_queue(r):
    client, p = r
    clock = Clock()
    queue = ReliableQueue(client, f"{p}:emails", clock=clock)
    ids = [queue.enqueue({"to": f"user{i}@example.com"}) for i in range(3)]
    assert len(set(ids)) == 3 and all(len(i) == 32 for i in ids)
    assert queue.ready_count() == 3

    first = queue.reserve(timeout=0.1)
    assert first is not None and first.id == ids[0] and first.payload == {"to": "user0@example.com"}
    assert queue.ready_count() == 2 and queue.processing_count() == 1
    queue.ack(first)
    assert queue.processing_count() == 0
    assert client.hlen(f"{p}:emails:reserved_at") == 0

    second = queue.reserve(timeout=0.1)
    clock.now += 30
    third = queue.reserve(timeout=0.1)
    assert (second.id, third.id) == (ids[1], ids[2])
    clock.now += 45
    assert queue.requeue_stale(older_than=60) == 1  # only `second` (75 s old)
    assert queue.processing_count() == 1 and queue.ready_count() == 1
    again = queue.reserve(timeout=0.1)
    assert again.id == ids[1]
    started = time.monotonic()
    assert queue.reserve(timeout=0.2) is None
    assert time.monotonic() - started >= 0.15


def test_run_once(r):
    client, p = r
    key = f"{p}:idem:midtrans:ORDER-17:settlement"
    calls = []

    def mark_paid():
        calls.append(1)
        return {"order": 17, "status": "paid"}

    assert run_once(client, key, 600, mark_paid) == ({"order": 17, "status": "paid"}, True)
    assert run_once(client, key, 600, mark_paid) == ({"order": 17, "status": "paid"}, False)
    assert calls == [1]
    assert 590 <= client.ttl(key) <= 600

    failing_key = f"{p}:idem:fail"

    def boom():
        raise RuntimeError("payment API down")

    with pytest.raises(RuntimeError):
        run_once(client, failing_key, 600, boom)
    assert client.exists(failing_key) == 0
    assert run_once(client, failing_key, 600, lambda: "ok") == ("ok", True)

    client.set(f"{p}:idem:busy", "__pending__", ex=60)
    with pytest.raises(InProgressError):
        run_once(client, f"{p}:idem:busy", 60, mark_paid)

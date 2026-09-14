"""Redis patterns. See README.md."""

from __future__ import annotations

import json
import math
import random
import secrets
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import redis


class InProgressError(Exception):
    """Another request with the same idempotency key is still running."""


# ---------- 1. cache-aside ----------

def cache_aside(r: redis.Redis, key: str, ttl: int, loader: Callable[[], Any], *, jitter: float = 0.1, rng: Callable[[], float] = random.random) -> Any:
    cached = r.get(key)
    if cached is not None:
        return json.loads(cached)
    value = loader()
    if value is None:
        return None  # don't cache "not found" by accident (or use a short negative TTL on purpose)
    # Jitter spreads expirations so thousands of keys don't expire in the same second.
    r.set(key, json.dumps(value), ex=ttl + int(ttl * jitter * rng()))
    return value


def invalidate(r: redis.Redis, *keys: str) -> int:
    return int(r.delete(*keys)) if keys else 0


# ---------- 2. stampede protection ----------

RELEASE_LOCK = """
if redis.call('GET', KEYS[1]) == ARGV[1] then
  return redis.call('DEL', KEYS[1])
end
return 0
"""


def cache_with_lock(r: redis.Redis, key: str, ttl: int, loader: Callable[[], Any], *, lock_ttl_ms: int = 5000, poll_interval: float = 0.02, max_wait: float = 2.0) -> Any:
    cached = r.get(key)
    if cached is not None:
        return json.loads(cached)

    lock_key, token = f"lock:{key}", secrets.token_hex(16)
    if r.set(lock_key, token, nx=True, px=lock_ttl_ms):
        try:
            cached = r.get(key)  # someone may have filled it between our GET and SET NX
            if cached is not None:
                return json.loads(cached)
            value = loader()
            r.set(key, json.dumps(value), ex=ttl)
            return value
        finally:
            # Only delete OUR lock: if loading took longer than lock_ttl_ms, another client may own it now.
            r.eval(RELEASE_LOCK, 1, lock_key, token)

    deadline = time.monotonic() + max_wait
    while time.monotonic() < deadline:
        time.sleep(poll_interval)
        cached = r.get(key)
        if cached is not None:
            return json.loads(cached)
    return loader()  # degrade gracefully instead of hanging the request


# ---------- 3. sliding-window rate limiter ----------

SLIDING_WINDOW = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local member = ARGV[4]
local ttl = tonumber(ARGV[5])
redis.call('ZREMRANGEBYSCORE', key, '-inf', now - window)
local count = redis.call('ZCARD', key)
if count < limit then
  redis.call('ZADD', key, now, member)
  redis.call('EXPIRE', key, ttl)
  return {1, '0'}
end
local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
redis.call('EXPIRE', key, ttl)
return {0, tostring(tonumber(oldest[2]) + window - now)}
"""


class SlidingWindowRateLimiter:
    def __init__(self, r: redis.Redis, *, limit: int, window_seconds: float, prefix: str = "ratelimit", clock: Callable[[], float] = time.time):
        self.r, self.limit, self.window, self.prefix, self.clock = r, limit, window_seconds, prefix, clock
        self._script = r.register_script(SLIDING_WINDOW)

    def allow(self, identity: str) -> tuple[bool, float]:
        now = self.clock()
        allowed, retry_after = self._script(
            keys=[f"{self.prefix}:{identity}"],
            args=[repr(now), self.window, self.limit, f"{now}:{uuid.uuid4().hex}", math.ceil(self.window)],
        )
        return bool(allowed), round(float(retry_after), 3)


# ---------- 4. reliable queue ----------

@dataclass(frozen=True)
class Job:
    id: str
    payload: dict
    raw: str


class ReliableQueue:
    def __init__(self, r: redis.Redis, name: str, *, clock: Callable[[], float] = time.time):
        self.r, self.clock = r, clock
        self.ready, self.processing, self.reserved_at = f"{name}:ready", f"{name}:processing", f"{name}:reserved_at"

    def enqueue(self, payload: dict) -> str:
        job_id = uuid.uuid4().hex
        self.r.lpush(self.ready, json.dumps({"id": job_id, "payload": payload}))
        return job_id

    def reserve(self, timeout: float = 1.0) -> Job | None:
        # Atomic move: if the worker crashes now, the job is still in "processing", not lost.
        raw = self.r.blmove(self.ready, self.processing, timeout, src="RIGHT", dest="LEFT")
        if raw is None:
            return None
        data = json.loads(raw)
        self.r.hset(self.reserved_at, data["id"], repr(self.clock()))
        return Job(data["id"], data["payload"], raw)

    def ack(self, job: Job) -> None:
        pipe = self.r.pipeline()
        pipe.lrem(self.processing, 1, job.raw)
        pipe.hdel(self.reserved_at, job.id)
        pipe.execute()

    def requeue_stale(self, older_than: float) -> int:
        cutoff = self.clock() - older_than
        moved = 0
        for raw in self.r.lrange(self.processing, 0, -1):
            job_id = json.loads(raw)["id"]
            reserved = self.r.hget(self.reserved_at, job_id)
            if reserved is not None and float(reserved) > cutoff:
                continue
            pipe = self.r.pipeline()
            pipe.lrem(self.processing, 1, raw)
            pipe.rpush(self.ready, raw)  # right end = next to be reserved
            pipe.hdel(self.reserved_at, job_id)
            removed, _, _ = pipe.execute()
            moved += int(removed > 0)
        return moved

    def ready_count(self) -> int:
        return int(self.r.llen(self.ready))

    def processing_count(self) -> int:
        return int(self.r.llen(self.processing))


# ---------- 5. idempotency ----------

PENDING = "__pending__"


def run_once(r: redis.Redis, key: str, ttl: int, action: Callable[[], Any]) -> tuple[Any, bool]:
    if r.set(key, PENDING, nx=True, ex=ttl):
        try:
            result = action()
        except Exception:
            r.delete(key)  # let a retry run the action again
            raise
        r.set(key, json.dumps(result), keepttl=True)
        return result, True
    stored = r.get(key)
    if stored is None:  # expired between SET and GET: treat as new
        return run_once(r, key, ttl, action)
    if stored == PENDING:
        raise InProgressError(key)
    return json.loads(stored), False

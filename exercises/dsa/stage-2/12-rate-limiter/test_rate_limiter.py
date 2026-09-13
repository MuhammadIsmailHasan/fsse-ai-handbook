import random
import time

from rate_limiter import RateLimiter


def test_example():
    limiter = RateLimiter(limit=3, window=10)
    assert [limiter.allow("siti", t) for t in (0, 1, 2, 3)] == [True, True, True, False]
    assert limiter.allow("budi", 3) is True
    assert limiter.allow("siti", 9.999) is False
    assert limiter.allow("siti", 10) is True
    assert limiter.allow("siti", 11) is True
    assert limiter.allow("siti", 12) is True
    assert limiter.allow("siti", 12.5) is False


def test_rejected_requests_are_not_recorded():
    limiter = RateLimiter(limit=1, window=5)
    assert limiter.allow("u", 0) is True
    assert all(limiter.allow("u", t) is False for t in (1, 2, 3, 4))
    assert limiter.allow("u", 5) is True, "rejections at t=1..4 must not extend the block"


def brute(events, limit, window):
    accepted = {}
    results = []
    for user, now in events:
        recent = [t for t in accepted.get(user, []) if now - t < window]
        ok = len(recent) < limit
        if ok:
            accepted.setdefault(user, []).append(now)
        results.append(ok)
    return results


def test_matches_brute_force():
    rng = random.Random(13)
    for _ in range(100):
        limit, window = rng.randint(1, 4), rng.choice([1, 2.5, 5])
        now, events = 0.0, []
        for _ in range(60):
            now += rng.choice([0, 0.5, 1, 2])
            events.append((rng.choice("ab"), now))
        limiter = RateLimiter(limit, window)
        assert [limiter.allow(user, t) for user, t in events] == brute(events, limit, window)


def test_stays_fast_with_big_windows():
    limiter = RateLimiter(limit=1_000, window=1_000_000)
    started = time.perf_counter()
    for i in range(300_000):
        limiter.allow("bot", i * 0.001)
    assert time.perf_counter() - started < 1.5, "don't rebuild or scan the whole log on every call"

from ratelimit_cache import CacheAside, TokenBucket


def test_bucket_allows_up_to_capacity_then_rejects():
    bucket = TokenBucket(capacity=3, refill_per_sec=1)
    assert bucket.allow(now=0) is True
    assert bucket.allow(now=0) is True
    assert bucket.allow(now=0) is True
    assert bucket.allow(now=0) is False  # empty → rejected (429)


def test_bucket_refills_over_time():
    bucket = TokenBucket(capacity=3, refill_per_sec=1)
    for _ in range(3):
        bucket.allow(now=0)
    assert bucket.allow(now=0) is False
    # After 2 seconds, ~2 tokens are back.
    assert bucket.allow(now=2) is True
    assert bucket.allow(now=2) is True
    assert bucket.allow(now=2) is False


def test_bucket_never_exceeds_capacity():
    bucket = TokenBucket(capacity=3, refill_per_sec=1)
    # Wait a long time: tokens cap at capacity, not 100.
    assert bucket.allow(now=100) is True
    bucket2 = TokenBucket(capacity=3, refill_per_sec=1)
    for _ in range(3):
        assert bucket2.allow(now=100) is True
    assert bucket2.allow(now=100) is False


def test_cache_aside_loads_only_on_miss():
    calls = {"n": 0}

    def loader():
        calls["n"] += 1
        return "PRODUCT"

    cache = CacheAside()
    value, status = cache.get("p1", now=0, ttl=10, loader=loader)
    assert (value, status) == ("PRODUCT", "miss") and calls["n"] == 1

    # Within TTL → hit, loader not called again.
    value, status = cache.get("p1", now=5, ttl=10, loader=loader)
    assert (value, status) == ("PRODUCT", "hit") and calls["n"] == 1

    # After TTL → miss, loader runs again.
    value, status = cache.get("p1", now=11, ttl=10, loader=loader)
    assert status == "miss" and calls["n"] == 2


def test_invalidate_forces_a_miss():
    calls = {"n": 0}

    def loader():
        calls["n"] += 1
        return "V"

    cache = CacheAside()
    cache.get("k", now=0, ttl=100, loader=loader)  # miss, n=1
    cache.get("k", now=1, ttl=100, loader=loader)  # hit, n=1
    cache.invalidate("k")                          # e.g. data was updated
    _, status = cache.get("k", now=2, ttl=100, loader=loader)
    assert status == "miss" and calls["n"] == 2

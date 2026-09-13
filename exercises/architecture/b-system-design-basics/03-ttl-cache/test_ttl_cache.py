from ttl_cache import TTLCache, cached_fetch


class FakeClock:
    def __init__(self):
        self.now = 1_000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def test_set_and_get_before_expiry():
    clock = FakeClock()
    cache = TTLCache(ttl_seconds=60, clock=clock)
    cache.set("job:1", {"title": "Backend Dev"})
    clock.advance(59)
    assert cache.get("job:1") == {"title": "Backend Dev"}
    assert (cache.hits, cache.misses) == (1, 0)


def test_expires_after_ttl():
    clock = FakeClock()
    cache = TTLCache(ttl_seconds=60, clock=clock)
    cache.set("job:1", "value")
    clock.advance(60)
    assert cache.get("job:1", default="gone") == "gone"
    assert cache.misses == 1


def test_set_again_refreshes_expiry():
    clock = FakeClock()
    cache = TTLCache(ttl_seconds=10, clock=clock)
    cache.set("k", 1)
    clock.advance(8)
    cache.set("k", 2)
    clock.advance(8)
    assert cache.get("k") == 2


def test_delete_and_missing_keys():
    cache = TTLCache(ttl_seconds=10, clock=FakeClock())
    cache.set("k", 1)
    cache.delete("k")
    cache.delete("never-existed")
    assert cache.get("k") is None
    assert cache.misses == 1


def test_cached_value_can_be_falsy():
    cache = TTLCache(ttl_seconds=10, clock=FakeClock())
    cache.set("count", 0)
    assert cache.get("count", default=-1) == 0
    assert cache.hits == 1


def test_cached_fetch_calls_source_once():
    clock = FakeClock()
    cache = TTLCache(ttl_seconds=30, clock=clock)
    calls = []

    def fetch():
        calls.append(1)
        return "fresh"

    assert cached_fetch(cache, "a", fetch) == "fresh"
    assert cached_fetch(cache, "a", fetch) == "fresh"
    assert len(calls) == 1
    clock.advance(31)
    cached_fetch(cache, "a", fetch)
    assert len(calls) == 2


def test_cached_fetch_does_not_cache_none():
    cache = TTLCache(ttl_seconds=30, clock=FakeClock())
    calls = []
    cached_fetch(cache, "missing", lambda: calls.append(1))
    cached_fetch(cache, "missing", lambda: calls.append(1))
    assert len(calls) == 2

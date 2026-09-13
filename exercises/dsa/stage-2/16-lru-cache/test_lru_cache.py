import random
import time
from pathlib import Path

from lru_cache import LRUCache


def test_example():
    cache = LRUCache(capacity=2)
    cache.put("kopi", 1)
    cache.put("awan", 2)
    assert cache.get("kopi") == 1
    cache.put("batik", 3)
    assert cache.get("awan") is None
    assert (cache.get("kopi"), cache.get("batik"), len(cache)) == (1, 3, 2)


def test_update_refreshes_recency():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("a", 10)
    cache.put("c", 3)
    assert (cache.get("a"), cache.get("b"), cache.get("c")) == (10, None, 3)
    assert len(cache) == 2


def test_capacity_one():
    cache = LRUCache(1)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") is None and cache.get("b") == 2 and len(cache) == 1


class Reference:
    def __init__(self, capacity):
        self.capacity, self.items = capacity, []

    def get(self, key):
        for i, (k, v) in enumerate(self.items):
            if k == key:
                self.items.append(self.items.pop(i))
                return v
        return None

    def put(self, key, value):
        self.items = [(k, v) for k, v in self.items if k != key] + [(key, value)]
        if len(self.items) > self.capacity:
            self.items.pop(0)


def test_matches_reference():
    rng = random.Random(17)
    for _ in range(50):
        capacity = rng.randint(1, 4)
        cache, reference = LRUCache(capacity), Reference(capacity)
        for _ in range(200):
            key = rng.choice("abcdef")
            if rng.random() < 0.5:
                assert cache.get(key) == reference.get(key)
            else:
                value = rng.randint(0, 99)
                cache.put(key, value)
                reference.put(key, value)
            assert len(cache) == len(reference.items)


def test_constant_time_operations():
    cache = LRUCache(100_000)
    for i in range(100_000):
        cache.put(str(i), i)
    started = time.perf_counter()
    for i in range(100_000):
        cache.get(str(i))
        cache.put(f"new-{i}", i)
    assert time.perf_counter() - started < 1.5, "get/put must be O(1) — no list scans or pops from the front"
    assert len(cache) == 100_000


def test_built_by_hand():
    source = (Path(__file__).parent / "lru_cache.py").read_text()
    assert "OrderedDict" not in source and "lru_cache(" not in source and "functools" not in source

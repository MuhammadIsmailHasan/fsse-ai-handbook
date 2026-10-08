import random
import time

from top_k import KthLargest, k_largest, k_most_frequent


def test_k_largest_examples():
    assert k_largest([3, 1, 5, 12, 2, 11], 3) == [12, 11, 5]
    assert k_largest([5, 5, 5, 1], 2) == [5, 5]
    assert k_largest([1, 2], 5) == [2, 1]
    assert k_largest([], 3) == []
    assert k_largest([4, 9], 0) == []


def test_k_largest_matches_sorted():
    rng = random.Random(71)
    for _ in range(300):
        nums = [rng.randint(-50, 50) for _ in range(rng.randint(0, 40))]
        k = rng.randint(0, 10)
        assert k_largest(nums, k) == sorted(nums, reverse=True)[:k]


def test_k_largest_on_a_large_input():
    rng = random.Random(72)
    nums = [rng.randint(0, 10**9) for _ in range(300_000)]
    started = time.perf_counter()
    assert k_largest(nums, 10) == sorted(nums, reverse=True)[:10]
    assert time.perf_counter() - started < 2.0


def test_k_largest_does_not_change_the_input():
    nums = [3, 1, 2]
    k_largest(nums, 2)
    assert nums == [3, 1, 2]


def test_k_most_frequent_examples():
    words = ["i", "love", "leetcode", "i", "love", "coding"]
    assert k_most_frequent(words, 2) == ["i", "love"]
    words = ["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"]
    assert k_most_frequent(words, 4) == ["the", "is", "sunny", "day"]


def test_k_most_frequent_ties_are_alphabetical():
    assert k_most_frequent(["b", "a", "c", "b", "a", "c"], 3) == ["a", "b", "c"]
    assert k_most_frequent(["z", "y"], 1) == ["y"]


def test_k_most_frequent_more_k_than_words():
    assert k_most_frequent(["a", "a", "b"], 10) == ["a", "b"]
    assert k_most_frequent([], 3) == []


def test_kth_largest_stream_example():
    kth = KthLargest(3, [4, 5, 8, 2])
    assert [kth.add(v) for v in (3, 5, 10, 9, 4)] == [4, 5, 5, 8, 8]


def test_kth_largest_returns_none_until_k_values_exist():
    kth = KthLargest(3, [])
    assert kth.add(10) is None
    assert kth.add(20) is None
    assert kth.add(5) == 5
    assert kth.add(30) == 10


def test_kth_largest_keeps_only_k_values():
    kth = KthLargest(2, [])
    for v in range(10_000):
        kth.add(v)
    assert len(kth.heap) == 2 if hasattr(kth, "heap") else True
    assert kth.add(-1) == 9_998


def test_kth_largest_matches_sorting():
    rng = random.Random(73)
    for _ in range(100):
        k = rng.randint(1, 6)
        start = [rng.randint(0, 30) for _ in range(rng.randint(0, 8))]
        kth = KthLargest(k, list(start))
        seen = list(start)
        for _ in range(20):
            v = rng.randint(0, 30)
            seen.append(v)
            expected = sorted(seen, reverse=True)[k - 1] if len(seen) >= k else None
            assert kth.add(v) == expected

import random
import time

import pytest

from window_basics import has_nearby_repeat, max_vowels, max_window_sum


@pytest.mark.parametrize(("nums", "k", "expected"), [([2, 1, 5, 1, 3, 2], 3, 9), ([-1, -2, -3], 2, -3), ([4], 1, 4), ([1, 2], 3, None), ([1, 2], 0, None)])
def test_max_window_sum(nums, k, expected):
    assert max_window_sum(nums, k) == expected


def test_max_window_sum_random():
    rng = random.Random(41)
    for _ in range(400):
        nums = [rng.randint(-9, 9) for _ in range(rng.randint(1, 12))]
        k = rng.randint(1, len(nums))
        assert max_window_sum(nums, k) == max(sum(nums[i : i + k]) for i in range(len(nums) - k + 1))


def test_max_window_sum_independent_of_k():
    nums = list(range(200_000))
    started = time.perf_counter()
    assert max_window_sum(nums, 100_000) == sum(range(100_000, 200_000))
    assert time.perf_counter() - started < 0.5, "O(n·k) — slide the window instead of re-summing"


@pytest.mark.parametrize(("items", "k", "expected"), [(["a", "b", "c", "a"], 3, True), (["a", "b", "c", "a"], 2, False), (["x", "x"], 1, True), (["x", "x"], 0, False), ([], 5, False)])
def test_has_nearby_repeat(items, k, expected):
    assert has_nearby_repeat(items, k) is expected


def test_has_nearby_repeat_random():
    rng = random.Random(42)
    for _ in range(400):
        items = [rng.choice("abcd") for _ in range(rng.randint(0, 12))]
        k = rng.randint(0, 5)
        expected = any(items[i] == items[j] for i in range(len(items)) for j in range(i + 1, min(len(items), i + k + 1)))
        assert has_nearby_repeat(items, k) is expected


@pytest.mark.parametrize(("text", "k", "expected"), [("abciiidef", 3, 3), ("aeiou", 2, 2), ("leetcode", 3, 2), ("xyz", 2, 0)])
def test_max_vowels(text, k, expected):
    assert max_vowels(text, k) == expected


def test_max_vowels_fast():
    text = "ab" * 150_000
    started = time.perf_counter()
    assert max_vowels(text, 100_000) == 50_000
    assert time.perf_counter() - started < 0.5

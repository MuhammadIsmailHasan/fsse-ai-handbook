import random
import time

import pytest

from prefix_basics import pivot_index, range_sums, running_totals


def test_running_totals():
    assert running_totals([3, 1, 4]) == [3, 4, 8]
    assert running_totals([]) == []
    assert running_totals([-2, 2]) == [-2, 0]


def test_range_sums_examples_and_random():
    assert range_sums([2, 4, 1, 5], [(0, 1), (1, 3), (2, 2)]) == [6, 10, 1]
    rng = random.Random(51)
    for _ in range(200):
        nums = [rng.randint(-9, 9) for _ in range(rng.randint(1, 12))]
        queries = [tuple(sorted((rng.randrange(len(nums)), rng.randrange(len(nums))))) for _ in range(10)]
        assert range_sums(nums, queries) == [sum(nums[i : j + 1]) for i, j in queries]


def test_range_sums_many_queries_fast():
    nums = list(range(100_000))
    queries = [(0, 99_999)] * 100_000
    started = time.perf_counter()
    assert range_sums(nums, queries)[0] == sum(nums)
    assert time.perf_counter() - started < 1.0, "O(n · q) — build a prefix array once"


@pytest.mark.parametrize(("nums", "expected"), [([1, 7, 3, 6, 5, 6], 3), ([1, 2, 3], -1), ([2, 1, -1], 0), ([0], 0), ([], -1), ([0, 0, 0], 0), ([-1, -1, 0, 1, 1, 0], 5)])
def test_pivot_index(nums, expected):
    assert pivot_index(nums) == expected


def test_pivot_random_and_linear():
    rng = random.Random(52)
    for _ in range(300):
        nums = [rng.randint(-3, 3) for _ in range(rng.randint(0, 10))]
        expected = next((i for i in range(len(nums)) if sum(nums[:i]) == sum(nums[i + 1 :])), -1)
        assert pivot_index(nums) == expected
    big = [1] * 200_001
    started = time.perf_counter()
    assert pivot_index(big) == 100_000
    assert time.perf_counter() - started < 0.5

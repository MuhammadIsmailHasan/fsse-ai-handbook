import random
import time

import pytest

from net_change import count_periods


def brute(nums, k):
    return sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums) + 1) if sum(nums[i:j]) == k)


@pytest.mark.parametrize(("nums", "k"), [([1, 1, 1], 2), ([3, 4, -7, 3, 1], 7), ([], 0), ([0, 0, 0], 0), ([1, -1, 0], 0), ([5], 5), ([1, 2, 3], 7)])
def test_examples(nums, k):
    assert count_periods(nums, k) == brute(nums, k)


def test_readme_examples():
    assert count_periods([1, 1, 1], 2) == 2
    assert count_periods([3, 4, -7, 7, 0], 7) == 5


def test_matches_brute_force():
    rng = random.Random(53)
    for _ in range(400):
        nums = [rng.randint(-4, 4) for _ in range(rng.randint(0, 14))]
        k = rng.randint(-5, 5)
        assert count_periods(nums, k) == brute(nums, k)


def test_linear():
    nums = [1, -1] * 100_000
    started = time.perf_counter()
    assert count_periods(nums, 0) == 100_000 * 100_000
    assert time.perf_counter() - started < 1.0

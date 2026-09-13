import random
import time

import pytest

from inversions import count_inversions


@pytest.mark.parametrize(("nums", "expected"), [([2, 4, 1, 3, 5], 3), ([1, 2, 3], 0), ([3, 2, 1], 3), ([], 0), ([1, 1, 1], 0), ([2, 1, 2, 1], 3)])
def test_examples(nums, expected):
    before = nums[:]
    assert count_inversions(nums) == expected
    assert nums == before


def test_matches_brute_force():
    rng = random.Random(78)
    for _ in range(300):
        nums = [rng.randint(0, 9) for _ in range(rng.randint(0, 20))]
        expected = sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums)) if nums[i] > nums[j])
        assert count_inversions(nums) == expected


def test_n_log_n():
    n = 150_000
    nums = list(range(n, 0, -1))
    started = time.perf_counter()
    assert count_inversions(nums) == n * (n - 1) // 2
    assert time.perf_counter() - started < 3.0, "O(n²) won't finish — count while merging"

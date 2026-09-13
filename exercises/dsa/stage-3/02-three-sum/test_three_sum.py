import itertools
import random
import time

import pytest

from three_sum import three_sum_zero


@pytest.mark.parametrize(
    ("nums", "expected"),
    [([-1, 0, 1, 2, -1, -4], [[-1, -1, 2], [-1, 0, 1]]), ([0, 0, 0, 0], [[0, 0, 0]]), ([0, 1, 1], []), ([], []), ([3, -3], [])],
)
def test_examples(nums, expected):
    assert three_sum_zero(nums) == expected


def brute(nums):
    return sorted({tuple(sorted(t)) for t in itertools.combinations(nums, 3) if sum(t) == 0})


def test_matches_brute_force():
    rng = random.Random(34)
    for _ in range(300):
        nums = [rng.randint(-6, 6) for _ in range(rng.randint(0, 12))]
        assert three_sum_zero(nums) == [list(t) for t in brute(nums)]


def test_does_not_modify_input():
    nums = [3, -1, -2]
    three_sum_zero(nums)
    assert nums == [3, -1, -2]


def test_quadratic_not_cubic():
    rng = random.Random(35)
    nums = [rng.randint(-100_000, 100_000) for _ in range(1_500)]
    started = time.perf_counter()
    three_sum_zero(nums)
    assert time.perf_counter() - started < 2.0, "O(n³) is too slow — sort + two pointers"

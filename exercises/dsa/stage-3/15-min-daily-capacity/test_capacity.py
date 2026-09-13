import random
import time

import pytest

from capacity import min_daily_capacity


@pytest.mark.parametrize(("sizes", "days", "expected"), [([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5, 15), ([3, 2, 2, 4, 1, 4], 3, 6), ([1, 2, 3, 1, 1], 4, 3), ([7], 1, 7), ([5, 5, 5], 3, 5), ([5, 5, 5], 1, 15)])
def test_examples(sizes, days, expected):
    assert min_daily_capacity(sizes, days) == expected


def brute(sizes, days):
    capacity = max(sizes)
    while True:
        used, load = 1, 0
        for size in sizes:
            if load + size > capacity:
                used, load = used + 1, 0
            load += size
        if used <= days:
            return capacity
        capacity += 1


def test_matches_brute_force():
    rng = random.Random(64)
    for _ in range(300):
        sizes = [rng.randint(1, 9) for _ in range(rng.randint(1, 10))]
        days = rng.randint(1, len(sizes))
        assert min_daily_capacity(sizes, days) == brute(sizes, days)


def test_large_values_fast():
    sizes = [10**9] * 20_000
    started = time.perf_counter()
    assert min_daily_capacity(sizes, 7) == 10**9 * 2_858
    assert time.perf_counter() - started < 3.0, "try capacities with binary search, not one by one"

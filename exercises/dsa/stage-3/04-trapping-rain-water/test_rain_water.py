import random
import time
import tracemalloc

import pytest

from rain_water import trapped_water


@pytest.mark.parametrize(("heights", "expected"), [([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1], 6), ([4, 2, 0, 3, 2, 5], 9), ([], 0), ([3], 0), ([1, 2, 3], 0), ([3, 0, 3], 3)])
def test_examples(heights, expected):
    assert trapped_water(heights) == expected


def brute(heights):
    return sum(max(0, min(max(heights[: i + 1]), max(heights[i:])) - h) for i, h in enumerate(heights))


def test_matches_brute_force():
    rng = random.Random(37)
    for _ in range(500):
        heights = [rng.randint(0, 6) for _ in range(rng.randint(0, 14))]
        assert trapped_water(heights) == brute(heights)


def test_linear_time_constant_space():
    heights = [0, 5] * 200_000
    tracemalloc.start()
    started = time.perf_counter()
    try:
        assert trapped_water(heights) == 5 * (200_000 - 1)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert time.perf_counter() - started < 3.0
    assert peak < 100_000, f"peak {peak} bytes — avoid left_max/right_max arrays"

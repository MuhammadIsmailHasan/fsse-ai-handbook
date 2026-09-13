import random
import time

import pytest

from banner import max_banner_area


@pytest.mark.parametrize(("heights", "expected"), [([1, 8, 6, 2, 5, 4, 8, 3, 7], 49), ([1, 1], 1), ([], 0), ([5], 0), ([4, 3, 2, 1, 4], 16), ([0, 0, 0], 0)])
def test_examples(heights, expected):
    assert max_banner_area(heights) == expected


def test_matches_brute_force():
    rng = random.Random(36)
    for _ in range(500):
        heights = [rng.randint(0, 10) for _ in range(rng.randint(0, 12))]
        expected = max((min(heights[i], heights[j]) * (j - i) for i in range(len(heights)) for j in range(i + 1, len(heights))), default=0)
        assert max_banner_area(heights) == expected


def test_linear():
    heights = list(range(1, 300_001))
    started = time.perf_counter()
    assert max_banner_area(heights) == 150_000 * 150_000
    assert time.perf_counter() - started < 1.0

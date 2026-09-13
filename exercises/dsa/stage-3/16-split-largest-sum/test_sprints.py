import itertools
import random
import time

import pytest

from sprints import min_heaviest_sprint


@pytest.mark.parametrize(("points", "k", "expected"), [([7, 2, 5, 10, 8], 2, 18), ([1, 2, 3, 4, 5], 2, 9), ([1, 4, 4], 3, 4), ([0, 0, 5], 2, 5), ([6], 1, 6)])
def test_examples(points, k, expected):
    assert min_heaviest_sprint(points, k) == expected


def brute(points, k):
    n = len(points)
    best = None
    for cuts in itertools.combinations(range(1, n), k - 1):
        bounds = (0, *cuts, n)
        heaviest = max(sum(points[a:b]) for a, b in zip(bounds, bounds[1:]))
        best = heaviest if best is None else min(best, heaviest)
    return best


def test_matches_brute_force():
    rng = random.Random(65)
    for _ in range(300):
        points = [rng.randint(0, 9) for _ in range(rng.randint(1, 9))]
        k = rng.randint(1, len(points))
        assert min_heaviest_sprint(points, k) == brute(points, k)


def test_fast():
    rng = random.Random(66)
    points = [rng.randint(0, 10**6) for _ in range(50_000)]
    started = time.perf_counter()
    min_heaviest_sprint(points, 50)
    assert time.perf_counter() - started < 3.0

import random
import time

from region_sums import RegionSums


def test_examples():
    sums = RegionSums([[3, 0, 1, 4], [5, 6, 3, 2], [1, 2, 0, 1]])
    assert sums.total(0, 0, 1, 1) == 14
    assert sums.total(1, 1, 2, 3) == 14
    assert sums.total(2, 3, 2, 3) == 1
    assert sums.total(0, 0, 2, 3) == 28


def test_matches_brute_force():
    rng = random.Random(54)
    for _ in range(50):
        rows, cols = rng.randint(1, 6), rng.randint(1, 6)
        grid = [[rng.randint(-5, 9) for _ in range(cols)] for _ in range(rows)]
        sums = RegionSums(grid)
        for _ in range(30):
            r1, r2 = sorted((rng.randrange(rows), rng.randrange(rows)))
            c1, c2 = sorted((rng.randrange(cols), rng.randrange(cols)))
            assert sums.total(r1, c1, r2, c2) == sum(grid[r][c] for r in range(r1, r2 + 1) for c in range(c1, c2 + 1))


def test_constant_time_queries():
    grid = [[1] * 300 for _ in range(300)]
    sums = RegionSums(grid)
    started = time.perf_counter()
    for _ in range(100_000):
        sums.total(0, 0, 299, 299)
    assert time.perf_counter() - started < 1.0, "queries must be O(1), not a loop over the rectangle"

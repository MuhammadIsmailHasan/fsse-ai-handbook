import random
import statistics
import time

import pytest

from median_ropes import MedianFinder, min_cost_to_connect


def test_median_empty():
    with pytest.raises(IndexError):
        MedianFinder().find_median()


def test_median_example():
    mf = MedianFinder()
    mf.add_num(1)
    assert mf.find_median() == 1
    mf.add_num(2)
    assert mf.find_median() == 1.5
    mf.add_num(3)
    assert mf.find_median() == 2


def test_median_returns_a_float_for_even_counts():
    mf = MedianFinder()
    for v in (2, 4):
        mf.add_num(v)
    assert mf.find_median() == 3.0
    assert isinstance(mf.find_median(), float)


def test_median_handles_negatives_and_duplicates():
    mf = MedianFinder()
    for v in (-5, -5, 0, 7, 7):
        mf.add_num(v)
    assert mf.find_median() == 0


def test_median_matches_statistics_after_every_add():
    rng = random.Random(91)
    for _ in range(100):
        mf, seen = MedianFinder(), []
        for _ in range(rng.randint(1, 40)):
            v = rng.randint(-100, 100)
            mf.add_num(v)
            seen.append(v)
            assert mf.find_median() == statistics.median(seen)


def test_median_is_fast_for_many_adds():
    rng = random.Random(92)
    mf = MedianFinder()
    started = time.perf_counter()
    for _ in range(100_000):
        mf.add_num(rng.randint(0, 10**9))
        mf.find_median()
    assert time.perf_counter() - started < 3.0


def test_ropes_examples():
    assert min_cost_to_connect([4, 3, 2, 6]) == 29
    assert min_cost_to_connect([1, 8, 3, 5]) == 30
    assert min_cost_to_connect([5, 5]) == 10


def test_ropes_edges():
    assert min_cost_to_connect([]) == 0
    assert min_cost_to_connect([7]) == 0


def test_ropes_does_not_change_the_input():
    ropes = [4, 3, 2, 6]
    min_cost_to_connect(ropes)
    assert ropes == [4, 3, 2, 6]


def test_ropes_matches_brute_force_on_small_inputs():
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def best(state):
        if len(state) <= 1:
            return 0
        options = []
        for i in range(len(state)):
            for j in range(i + 1, len(state)):
                rest = [x for k, x in enumerate(state) if k not in (i, j)]
                joined = state[i] + state[j]
                options.append(joined + best(tuple(sorted(rest + [joined]))))
        return min(options)

    rng = random.Random(93)
    for _ in range(60):
        ropes = [rng.randint(1, 12) for _ in range(rng.randint(0, 6))]
        assert min_cost_to_connect(ropes) == best(tuple(sorted(ropes)))


def test_ropes_many_ropes_is_fast():
    rng = random.Random(94)
    ropes = [rng.randint(1, 1000) for _ in range(100_000)]
    started = time.perf_counter()
    min_cost_to_connect(ropes)
    assert time.perf_counter() - started < 3.0

import ast
import random
import time
from pathlib import Path

import pytest

from longest_streak import longest_streak


@pytest.mark.parametrize(
    ("days", "expected"),
    [([100, 4, 200, 1, 3, 2], 4), ([0, 3, 7, 2, 5, 8, 4, 6, 0, 1], 9), ([], 0), ([5], 1), ([1, 1, 1], 1), ([-2, -1, 0, 10], 3)],
)
def test_examples(days, expected):
    assert longest_streak(days) == expected


def brute(days):
    best = 0
    ordered = sorted(set(days))
    run = 0
    for i, day in enumerate(ordered):
        run = run + 1 if i and ordered[i - 1] == day - 1 else 1
        best = max(best, run)
    return best


def test_matches_brute_force():
    rng = random.Random(4)
    for _ in range(300):
        days = [rng.randint(-5, 15) for _ in range(rng.randint(0, 15))]
        assert longest_streak(days) == brute(days)


def test_is_linear_even_for_one_long_streak():
    days = list(range(300_000, 0, -1))
    started = time.perf_counter()
    assert longest_streak(days) == 300_000
    assert time.perf_counter() - started < 1.0, "only count upward from streak starts"


def test_does_not_sort():
    tree = ast.parse((Path(__file__).parent / "longest_streak.py").read_text())
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert not names & {"sorted", "sort"}, "solve it without sorting"

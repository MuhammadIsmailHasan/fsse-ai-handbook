import random
import time

import pytest

from affordable import longest_affordable


@pytest.mark.parametrize(("costs", "budget", "expected"), [([3, 1, 2, 7, 4, 2, 1, 1, 5], 8, 4), ([10, 20], 5, 0), ([], 3, 0), ([1, 1, 1], 3, 3), ([5], 5, 1), ([2, 9, 2], 4, 1)])
def test_examples(costs, budget, expected):
    assert longest_affordable(costs, budget) == expected


def test_matches_brute_force():
    rng = random.Random(44)
    for _ in range(400):
        costs = [rng.randint(1, 9) for _ in range(rng.randint(0, 14))]
        budget = rng.randint(0, 25)
        expected = max((j - i for i in range(len(costs)) for j in range(i + 1, len(costs) + 1) if sum(costs[i:j]) <= budget), default=0)
        assert longest_affordable(costs, budget) == expected


def test_linear():
    costs = [1] * 300_000
    started = time.perf_counter()
    assert longest_affordable(costs, 150_000) == 150_000
    assert time.perf_counter() - started < 1.0

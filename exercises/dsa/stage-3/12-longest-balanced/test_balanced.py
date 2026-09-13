import random
import time

import pytest

from balanced import longest_balanced


@pytest.mark.parametrize(("visits", "expected"), [([0, 1, 0], 2), ([0, 0, 1, 0, 1, 1, 0], 6), ([1, 1, 1], 0), ([], 0), ([1, 0], 2), ([0, 1, 1, 0, 1, 0], 6)])
def test_examples(visits, expected):
    assert longest_balanced(visits) == expected


def test_matches_brute_force():
    rng = random.Random(55)
    for _ in range(400):
        visits = [rng.randint(0, 1) for _ in range(rng.randint(0, 14))]
        expected = max((j - i for i in range(len(visits)) for j in range(i + 1, len(visits) + 1) if visits[i:j].count(0) == visits[i:j].count(1)), default=0)
        assert longest_balanced(visits) == expected


def test_linear():
    visits = [1] * 100_000 + [0, 1] * 100_000
    started = time.perf_counter()
    assert longest_balanced(visits) == 200_000
    assert time.perf_counter() - started < 1.0

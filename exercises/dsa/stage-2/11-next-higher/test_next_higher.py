import random
import time

import pytest

from next_higher import days_until_higher


@pytest.mark.parametrize(
    ("prices", "expected"),
    [([73, 74, 75, 71, 69, 72, 76, 73], [1, 1, 4, 2, 1, 1, 0, 0]), ([], []), ([5], [0]), ([3, 3, 3], [0, 0, 0]), ([1, 2, 3], [1, 1, 0]), ([3, 2, 1], [0, 0, 0])],
)
def test_examples(prices, expected):
    assert days_until_higher(prices) == expected


def brute(prices):
    return [next((j - i for j in range(i + 1, len(prices)) if prices[j] > prices[i]), 0) for i in range(len(prices))]


def test_matches_brute_force():
    rng = random.Random(10)
    for _ in range(300):
        prices = [rng.randint(0, 6) for _ in range(rng.randint(0, 15))]
        assert days_until_higher(prices) == brute(prices)


def test_is_linear_on_worst_case_for_brute_force():
    prices = list(range(200_000, 0, -1)) + [300_000]
    started = time.perf_counter()
    answer = days_until_higher(prices)
    assert answer[0] == 200_000 and answer[-1] == 0
    assert time.perf_counter() - started < 1.0, "Too slow — use a monotonic stack"

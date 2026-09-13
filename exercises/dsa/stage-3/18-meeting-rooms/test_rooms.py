import random
import time

import pytest

from rooms import rooms_needed


@pytest.mark.parametrize(("interviews", "expected"), [([(0, 30), (5, 10), (15, 20)], 2), ([(7, 10), (2, 4)], 1), ([], 0), ([(9, 10), (10, 11)], 1), ([(1, 5), (1, 5), (1, 5)], 3), ([(1, 4), (2, 3), (3, 6), (5, 7)], 2)])
def test_examples(interviews, expected):
    assert rooms_needed(interviews) == expected


def test_matches_brute_force():
    rng = random.Random(75)
    for _ in range(400):
        interviews = []
        for _ in range(rng.randint(0, 10)):
            a = rng.randint(0, 20)
            interviews.append((a, a + rng.randint(1, 6)))
        expected = max((sum(1 for a, b in interviews if a <= t < b) for t in range(0, 30)), default=0)
        assert rooms_needed(interviews) == expected


def test_fast():
    rng = random.Random(76)
    interviews = [(s, s + rng.randint(1, 100)) for s in (rng.randint(0, 10**6) for _ in range(200_000))]
    started = time.perf_counter()
    rooms_needed(interviews)
    assert time.perf_counter() - started < 2.0

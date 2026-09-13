import random
import time
from collections import Counter

import pytest

from top_k_skills import top_k_skills


@pytest.mark.parametrize(
    ("searches", "k", "expected"),
    [
        (["python", "sql", "python", "react", "sql", "python", "go"], 2, [("python", 3), ("sql", 2)]),
        (["b", "a", "c"], 2, [("a", 1), ("b", 1)]),
        (["x"], 5, [("x", 1)]),
        ([], 3, []),
        (["a", "a"], 0, []),
    ],
)
def test_examples(searches, k, expected):
    assert top_k_skills(searches, k) == expected


def test_matches_sorting_reference():
    rng = random.Random(12)
    for _ in range(300):
        searches = [rng.choice("abcdefg") for _ in range(rng.randint(0, 25))]
        k = rng.randint(0, 8)
        expected = sorted(Counter(searches).items(), key=lambda item: (-item[1], item[0]))[:k]
        assert top_k_skills(searches, k) == expected


def test_many_distinct_terms_small_k():
    searches = [f"term-{i:06d}" for i in range(400_000)] + ["term-000123"] * 3
    started = time.perf_counter()
    assert top_k_skills(searches, 1) == [("term-000123", 4)]
    assert time.perf_counter() - started < 2.0

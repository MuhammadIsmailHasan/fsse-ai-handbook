import random
import time
from collections import Counter

import pytest

from covering import shortest_covering


@pytest.mark.parametrize(
    ("text", "required", "expected"),
    [("ADOBECODEBANC", "ABC", "BANC"), ("aa", "aa", "aa"), ("a", "aa", ""), ("abc", "", ""), ("", "a", ""), ("aXbXa", "ab", "aXb"), ("bba", "ab", "ba")],
)
def test_examples(text, required, expected):
    assert shortest_covering(text, required) == expected


def brute(text, required):
    if not required:
        return ""
    need = Counter(required)
    for length in range(len(required), len(text) + 1):
        for start in range(len(text) - length + 1):
            window = Counter(text[start : start + length])
            if all(window[c] >= n for c, n in need.items()):
                return text[start : start + length]
    return ""


def test_matches_brute_force():
    rng = random.Random(45)
    for _ in range(400):
        text = "".join(rng.choice("abc") for _ in range(rng.randint(0, 12)))
        required = "".join(rng.choice("abc") for _ in range(rng.randint(0, 4)))
        assert shortest_covering(text, required) == brute(text, required)


def test_linear():
    text = "x" * 200_000 + "abc" + "y" * 200_000
    started = time.perf_counter()
    assert shortest_covering(text, "cba") == "abc"
    assert time.perf_counter() - started < 1.5

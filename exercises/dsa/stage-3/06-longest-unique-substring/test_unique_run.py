import random
import string
import time

import pytest

from unique_run import longest_unique_run


@pytest.mark.parametrize(("text", "expected"), [("abcabcbb", 3), ("bbbbb", 1), ("pwwkew", 3), ("", 0), ("abba", 2), ("dvdf", 3), (" ", 1)])
def test_examples(text, expected):
    assert longest_unique_run(text) == expected


def test_matches_brute_force():
    rng = random.Random(43)
    for _ in range(400):
        text = "".join(rng.choice("abcd") for _ in range(rng.randint(0, 14)))
        expected = max((j - i for i in range(len(text) + 1) for j in range(i, len(text) + 1) if len(set(text[i:j])) == j - i), default=0)
        assert longest_unique_run(text) == expected


def test_linear():
    text = (string.ascii_letters + string.digits) * 10_000
    started = time.perf_counter()
    assert longest_unique_run(text) == 62
    assert time.perf_counter() - started < 1.0

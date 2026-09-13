import random
import time
from pathlib import Path

import pytest

from common_prefix import longest_common_prefix


@pytest.mark.parametrize(
    ("words", "expected"),
    [
        (["backend-engineer-jakarta", "backend-engineer-remote", "backend-dev"], "backend-"),
        (["data", "devops"], "d"),
        (["ml", "ai"], ""),
        ([], ""),
        (["solo"], "solo"),
        (["same", "same"], "same"),
        (["abc", "ab", "abcd"], "ab"),
        (["", "anything"], ""),
    ],
)
def test_examples(words, expected):
    assert longest_common_prefix(words) == expected


def brute(words):
    if not words:
        return ""
    prefix = ""
    for length in range(1, min(map(len, words)) + 1):
        candidate = words[0][:length]
        if all(w.startswith(candidate) for w in words):
            prefix = candidate
        else:
            break
    return prefix


def test_matches_brute_force():
    rng = random.Random(3)
    for _ in range(300):
        base = "".join(rng.choice("ab") for _ in range(rng.randint(0, 6)))
        words = [base[: rng.randint(0, len(base))] + "".join(rng.choice("ab") for _ in range(rng.randint(0, 3))) for _ in range(rng.randint(1, 6))]
        assert longest_common_prefix(words) == brute(words)


def test_stops_early():
    words = ["x" + "a" * 100_000] + ["y" + "a" * 100_000] * 2_000
    started = time.perf_counter()
    assert longest_common_prefix(words) == ""
    assert time.perf_counter() - started < 0.5, "stop at the first mismatch instead of comparing whole words"


def test_no_commonprefix_shortcut():
    assert "commonprefix" not in (Path(__file__).parent / "common_prefix.py").read_text()

import time

import pytest

from first_unique import first_unique_index


@pytest.mark.parametrize(
    ("text", "expected"),
    [("pipeline", 4), ("careerpilot", 0), ("aabb", -1), ("", -1), ("z", 0), ("aAb", 0), ("abcabcd", 6)],
)
def test_examples(text, expected):
    assert first_unique_index(text) == expected


def test_is_linear_time():
    text = "ab" * 50_000 + "c"
    started = time.perf_counter()
    assert first_unique_index(text) == 100_000
    assert time.perf_counter() - started < 0.5, "Too slow — avoid text.count() inside a loop"

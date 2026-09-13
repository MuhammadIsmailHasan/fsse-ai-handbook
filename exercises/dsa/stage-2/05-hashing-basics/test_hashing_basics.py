import ast
import random
import time
from collections import Counter
from pathlib import Path

import pytest

from hashing_basics import common_skills, first_repeat, is_anagram


@pytest.mark.parametrize(
    ("items", "expected"),
    [(["js", "py", "go", "py", "js"], "py"), (["a", "b"], None), ([], None), (["x", "x"], "x"), (["a", "b", "c", "b", "a"], "b")],
)
def test_first_repeat(items, expected):
    assert first_repeat(items) == expected


def test_first_repeat_is_linear():
    items = [str(i) for i in range(200_000)] + ["0"]
    started = time.perf_counter()
    assert first_repeat(items) == "0"
    assert time.perf_counter() - started < 0.5, "`x in list` is O(n) — use a set"


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [("listen", "silent", True), ("aab", "abb", False), ("", "", True), ("Tea", "eat", False), ("a b", "ba ", True), ("abc", "abcd", False)],
)
def test_is_anagram(a, b, expected):
    assert is_anagram(a, b) is expected


def test_is_anagram_matches_counter():
    rng = random.Random(9)
    for _ in range(500):
        a = "".join(rng.choice("abc") for _ in range(rng.randint(0, 6)))
        b = "".join(rng.choice("abc") for _ in range(rng.randint(0, 6)))
        assert is_anagram(a, b) is (Counter(a) == Counter(b))


def test_is_anagram_counts_instead_of_sorting():
    tree = ast.parse((Path(__file__).parent / "hashing_basics.py").read_text())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "is_anagram")
    names = {n.id for n in ast.walk(function) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(function) if isinstance(n, ast.Attribute)}
    assert not names & {"sorted", "sort"}, "count characters with a dict instead of sorting (O(n) vs O(n log n))"


@pytest.mark.parametrize(
    ("mine", "wanted", "expected"),
    [
        (["sql", "python", "sql"], ["python", "docker", "sql"], ["python", "sql"]),
        ([], ["python"], []),
        (["go"], ["go", "go", "go"], ["go"]),
        (["a", "b"], ["c"], []),
    ],
)
def test_common_skills(mine, wanted, expected):
    assert common_skills(mine, wanted) == expected


def test_common_skills_is_linear():
    mine = [f"skill-{i}" for i in range(100_000)]
    wanted = [f"skill-{i}" for i in range(99_999, -1, -1)]
    started = time.perf_counter()
    assert len(common_skills(mine, wanted)) == 100_000
    assert time.perf_counter() - started < 0.5

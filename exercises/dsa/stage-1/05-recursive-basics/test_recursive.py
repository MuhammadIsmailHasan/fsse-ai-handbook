import ast
from pathlib import Path

import pytest

from recursive import count_down, is_palindrome, power, sum_digits


@pytest.mark.parametrize(("n", "expected"), [(0, 0), (7, 7), (4071, 12), (99999, 45)])
def test_sum_digits(n, expected):
    assert sum_digits(n) == expected


@pytest.mark.parametrize(("base", "exp", "expected"), [(2, 10, 1024), (5, 0, 1), (3, 1, 3), (7, 3, 343)])
def test_power(base, exp, expected):
    assert power(base, exp) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [("racecar", True), ("abba", True), ("", True), ("a", True), ("ab", False), ("Aba", False)],
)
def test_is_palindrome(text, expected):
    assert is_palindrome(text) is expected


def test_count_down():
    assert count_down(3) == [3, 2, 1, 0]
    assert count_down(0) == [0]


def test_uses_recursion_not_loops():
    tree = ast.parse(Path(__file__).with_name("recursive.py").read_text())
    assert not any(isinstance(n, (ast.For, ast.While, ast.comprehension)) for n in ast.walk(tree)), "No loops!"
    for func in (n for n in tree.body if isinstance(n, ast.FunctionDef)):
        calls = {c.func.id for c in ast.walk(func) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}
        assert func.name in calls, f"{func.name} should call itself"

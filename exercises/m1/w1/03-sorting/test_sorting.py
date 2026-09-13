"""Automatic checks. Don't edit — make them pass by editing sorting.py."""

import ast
import random
from pathlib import Path

from sorting import insertion_sort, newest_first, sort_names, top_paying

JOBS = [
    {"title": "QA", "salary": 7_000_000, "posted": "2026-08-01"},
    {"title": "Backend", "salary": 9_500_000, "posted": None},
    {"title": "Analyst", "salary": 9_500_000, "posted": "2026-09-10"},
    {"title": "ML", "salary": 15_000_000, "posted": "2026-09-01"},
    {"title": "Support", "salary": 5_000_000, "posted": None},
]


def test_insertion_sort_sorts():
    assert insertion_sort([5, 2, 4, 1]) == [1, 2, 4, 5]
    assert insertion_sort([]) == []
    assert insertion_sort([3, 3, -1]) == [-1, 3, 3]
    data = [random.randint(-100, 100) for _ in range(200)]
    assert insertion_sort(data) == sorted(data)


def test_insertion_sort_does_not_modify_input():
    original = [3, 1, 2]
    insertion_sort(original)
    assert original == [3, 1, 2]


def test_insertion_sort_is_hand_written():
    tree = ast.parse(Path(__file__).with_name("sorting.py").read_text())
    func = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "insertion_sort")
    names = {n.id for n in ast.walk(func) if isinstance(n, ast.Name)}
    attrs = {n.attr for n in ast.walk(func) if isinstance(n, ast.Attribute)}
    assert "sorted" not in names and "sort" not in attrs


def test_top_paying_with_tie_breaker():
    assert [job["title"] for job in top_paying(JOBS, 3)] == ["ML", "Analyst", "Backend"]
    assert top_paying(JOBS, 0) == []


def test_sort_names_case_insensitive():
    assert sort_names(["budi", "Citra", "ana"]) == ["ana", "budi", "Citra"]


def test_newest_first_puts_missing_dates_last():
    assert [job["title"] for job in newest_first(JOBS)] == ["Analyst", "ML", "QA", "Backend", "Support"]

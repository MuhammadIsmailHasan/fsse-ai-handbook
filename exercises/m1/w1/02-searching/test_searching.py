"""Automatic checks. Don't edit — make them pass by editing searching.py."""

import ast
from pathlib import Path

import pytest

from searching import binary_search, build_index, first_job_over, jobs_in_salary_range, linear_search

JOBS = [
    {"id": 101, "title": "QA Engineer", "salary": 7_000_000},
    {"id": 102, "title": "Backend Dev", "salary": 9_500_000},
    {"id": 103, "title": "Data Analyst", "salary": 8_000_000},
    {"id": 104, "title": "ML Engineer", "salary": 15_000_000},
]
SORTED_JOBS = sorted(JOBS, key=lambda job: job["salary"])


def test_linear_search():
    assert linear_search([5, 3, 9], 9) == 2
    assert linear_search(["a", "b", "a"], "a") == 0
    assert linear_search([], 1) == -1
    assert linear_search([1, 2], 7) == -1


def test_linear_search_writes_the_loop():
    tree = ast.parse(Path(__file__).with_name("searching.py").read_text())
    func = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "linear_search")
    assert not any(isinstance(n, ast.Compare) and any(isinstance(op, ast.In) for op in n.ops) for n in ast.walk(func))
    assert not any(isinstance(n, ast.Attribute) and n.attr == "index" for n in ast.walk(func))


NUMBERS = [3, 8, 15, 23, 42, 57, 91]


@pytest.mark.parametrize(("target", "index"), [(3, 0), (23, 3), (57, 5), (91, 6), (4, -1), (100, -1)])
def test_binary_search_finds_index(target, index):
    assert binary_search(NUMBERS, target)[0] == index


def test_binary_search_is_fast():
    big = list(range(0, 2_000_000, 2))  # one million sorted numbers
    index, steps = binary_search(big, 1_234_568)
    assert index == 617_284
    assert steps <= 21
    assert binary_search([], 5) == (-1, 0)


def test_first_job_over():
    assert first_job_over(JOBS, 9_000_000)["id"] == 102
    assert first_job_over(JOBS, 20_000_000) is None


def test_build_index():
    index = build_index(JOBS)
    assert index[104]["title"] == "ML Engineer"
    assert len(index) == 4


def test_jobs_in_salary_range_inclusive():
    ids = [job["id"] for job in jobs_in_salary_range(SORTED_JOBS, 8_000_000, 9_500_000)]
    assert ids == [103, 102]
    assert jobs_in_salary_range(SORTED_JOBS, 1, 2) == []
    assert len(jobs_in_salary_range(SORTED_JOBS, 0, 99_000_000)) == 4

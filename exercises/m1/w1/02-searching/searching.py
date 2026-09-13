"""M1 · W1 · 02 — Search tools."""

import bisect  # noqa: F401  (you'll need it for jobs_in_salary_range)

Job = dict[str, object]


def linear_search(items: list, target) -> int:
    """Index of target, or -1. Don't use `in` or .index()."""
    # YOUR CODE HERE
    return -2


def binary_search(sorted_items: list[int], target: int) -> tuple[int, int]:
    """Return (index or -1, number of comparisons against mid)."""
    # YOUR CODE HERE
    return (-2, 0)


def first_job_over(jobs: list[Job], minimum_salary: int) -> Job | None:
    # YOUR CODE HERE
    return {}


def build_index(jobs: list[Job]) -> dict[object, Job]:
    """{job["id"]: job}"""
    # YOUR CODE HERE
    return {}


def jobs_in_salary_range(jobs_sorted_by_salary: list[Job], low: int, high: int) -> list[Job]:
    """All jobs with low <= salary <= high. Input is sorted by salary. Use bisect."""
    # YOUR CODE HERE
    return []

"""Reference solution — compare AFTER a real attempt."""

import bisect

Job = dict[str, object]


def linear_search(items: list, target) -> int:
    for index, item in enumerate(items):
        if item == target:
            return index
    return -1


def binary_search(sorted_items: list[int], target: int) -> tuple[int, int]:
    low, high = 0, len(sorted_items) - 1
    steps = 0
    while low <= high:
        mid = (low + high) // 2
        steps += 1
        if sorted_items[mid] == target:
            return mid, steps
        if sorted_items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1, steps


def first_job_over(jobs: list[Job], minimum_salary: int) -> Job | None:
    return next((job for job in jobs if job["salary"] >= minimum_salary), None)


def build_index(jobs: list[Job]) -> dict[object, Job]:
    return {job["id"]: job for job in jobs}


def jobs_in_salary_range(jobs_sorted_by_salary: list[Job], low: int, high: int) -> list[Job]:
    salaries = [job["salary"] for job in jobs_sorted_by_salary]
    start = bisect.bisect_left(salaries, low)
    end = bisect.bisect_right(salaries, high)
    return jobs_sorted_by_salary[start:end]


def binary_search_first(sorted_items: list[int], target: int) -> int:
    """Stretch goal: keep searching LEFT after a match."""
    low, high, found = 0, len(sorted_items) - 1, -1
    while low <= high:
        mid = (low + high) // 2
        if sorted_items[mid] == target:
            found = mid
            high = mid - 1
        elif sorted_items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return found

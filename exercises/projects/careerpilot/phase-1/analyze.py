"""CareerPilot Phase 1 — analysis functions.

Rules: no print() here, and no file reading except in load_jobs().
See the handbook brief for every requirement.
"""

from datetime import date  # noqa: F401  (you'll need it)

Job = dict


def load_jobs(path: str) -> list[Job]:
    # YOUR CODE HERE (hint: csv.DictReader)
    return []


def filter_jobs(
    jobs: list[Job],
    city: str | None = None,
    remote: bool | None = None,
    min_salary: int | None = None,
) -> list[Job]:
    # YOUR CODE HERE
    return []


def top_skills(jobs: list[Job], n: int) -> list[tuple[str, int]]:
    # YOUR CODE HERE
    return []


def salary_stats(jobs: list[Job]) -> dict[str, int]:
    # YOUR CODE HERE
    return {}


def jobs_by_city(jobs: list[Job]) -> dict[str, int]:
    # YOUR CODE HERE
    return {}


def format_rupiah_number(amount: int) -> str:
    # YOUR CODE HERE
    return ""


def format_report(jobs: list[Job], top_n: int = 5) -> str:
    # YOUR CODE HERE
    return ""

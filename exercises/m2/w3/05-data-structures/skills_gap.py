"""M2 · W3 · 05 — Skills gap engine."""

from collections import Counter, defaultdict, deque  # noqa: F401
from dataclasses import dataclass  # noqa: F401


class JobListing:
    # YOUR CODE HERE: make this a frozen, slotted dataclass with a from_dict classmethod
    pass


def match_score(job, my_skills) -> float:
    # YOUR CODE HERE
    return 0.0


def missing_skills(job, my_skills) -> list[str]:
    # YOUR CODE HERE
    return []


def missing_skill_demand(jobs, my_skills) -> Counter:
    # YOUR CODE HERE
    return Counter()


def jobs_by_company(jobs) -> dict:
    # YOUR CODE HERE
    return {}


def best_matches(jobs, my_skills, n: int) -> list:
    # YOUR CODE HERE
    return []


class RecentlyViewed:
    # YOUR CODE HERE
    def __init__(self, limit: int):
        pass

    def add(self, job_id: int) -> None:
        pass

    def items(self) -> list[int]:
        return []

"""Reference solution."""

from collections import Counter, defaultdict, deque
from collections.abc import Iterable
from dataclasses import dataclass


def normalize_skills(skills: Iterable[str]) -> frozenset[str]:
    return frozenset(skill.strip().lower() for skill in skills if skill.strip())


@dataclass(frozen=True, slots=True)
class JobListing:
    id: int
    title: str
    company: str
    required_skills: frozenset[str]

    @classmethod
    def from_dict(cls, data: dict) -> "JobListing":
        return cls(
            id=data["id"],
            title=data["title"],
            company=data["company"],
            required_skills=normalize_skills(data["required_skills"]),
        )


def match_score(job: JobListing, my_skills: Iterable[str]) -> float:
    if not job.required_skills:
        return 1.0
    return len(job.required_skills & normalize_skills(my_skills)) / len(job.required_skills)


def missing_skills(job: JobListing, my_skills: Iterable[str]) -> list[str]:
    return sorted(job.required_skills - normalize_skills(my_skills))


def missing_skill_demand(jobs: Iterable[JobListing], my_skills: Iterable[str]) -> Counter:
    mine = normalize_skills(my_skills)
    demand: Counter = Counter()
    for job in jobs:
        demand.update(job.required_skills - mine)
    return demand


def jobs_by_company(jobs: Iterable[JobListing]) -> dict[str, list[JobListing]]:
    grouped: defaultdict[str, list[JobListing]] = defaultdict(list)
    for job in jobs:
        grouped[job.company].append(job)
    return dict(grouped)  # a plain dict so reading a missing company doesn't create it


def best_matches(jobs: Iterable[JobListing], my_skills: Iterable[str], n: int) -> list[JobListing]:
    mine = normalize_skills(my_skills)
    return sorted(jobs, key=lambda job: (-match_score(job, mine), job.id))[:n]


class RecentlyViewed:
    def __init__(self, limit: int):
        self._ids: deque[int] = deque(maxlen=limit)

    def add(self, job_id: int) -> None:
        if job_id in self._ids:  # small, bounded deque → cheap
            self._ids.remove(job_id)
        self._ids.appendleft(job_id)

    def items(self) -> list[int]:
        return list(self._ids)

"""Domain: pure business concepts and rules. Imports nothing from outer layers and does no I/O."""

from dataclasses import dataclass


@dataclass(frozen=True)
class JobPosting:
    id: str
    title: str
    company: str
    salary_max: int | None
    skills: tuple[str, ...]


def match_score(job: JobPosting, my_skills: list[str]) -> float:
    wanted = {s.lower() for s in job.skills}
    mine = {s.lower() for s in my_skills}
    return len(wanted & mine) / len(wanted) if wanted else 0.0

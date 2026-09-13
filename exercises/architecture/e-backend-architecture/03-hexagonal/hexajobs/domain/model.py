import json  # 🚩 I/O in the domain

from dataclasses import dataclass

from hexajobs.adapters.console_notifier import ConsoleNotifier  # 🚩 domain depends on an adapter


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


def load_jobs(path):  # 🚩 file parsing belongs in an adapter
    with open(path) as f:
        return [JobPosting(d["id"], d["title"], d["company"], d.get("salary_max"), tuple(s.lower() for s in d["skills"])) for d in json.load(f)]


def notify_matches(email, jobs, stream):  # 🚩 delivery belongs in an adapter
    ConsoleNotifier(stream).notify(email, jobs)

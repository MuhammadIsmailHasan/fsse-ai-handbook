"""Text reports. Depends on analysis and models."""

from .analysis import top_skills
from .models import JobListing


def format_report(jobs: list[JobListing], n: int) -> str:
    lines = [f"Top skills across {len(jobs)} job(s):"]
    lines += [f"{rank}. {skill} ({count})" for rank, (skill, count) in enumerate(top_skills(jobs, n), start=1)]
    return "\n".join(lines)

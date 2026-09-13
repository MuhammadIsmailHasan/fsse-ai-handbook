"""Analysis logic. Depends only on models."""

from collections import Counter

from .models import JobListing


def top_skills(jobs: list[JobListing], n: int) -> list[tuple[str, int]]:
    counts = Counter(skill for job in jobs for skill in job.skills)
    return sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))[:n]

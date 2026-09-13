"""Use cases: orchestrate domain rules through ports. No knowledge of files, consoles or databases."""

from hexajobs.application.ports import JobFeed, JobStore, Notifier
from hexajobs.domain.model import JobPosting, match_score


class ImportJobs:
    def __init__(self, feed: JobFeed, store: JobStore):
        self.feed, self.store = feed, store

    def __call__(self) -> int:
        existing = {job.id for job in self.store.all()}
        new: list[JobPosting] = []
        for job in self.feed.fetch_jobs():
            if job.id not in existing:
                new.append(job)
                existing.add(job.id)
        self.store.save_all(new)
        return len(new)


class RecommendJobs:
    def __init__(self, store: JobStore, notifier: Notifier):
        self.store, self.notifier = store, notifier

    def __call__(self, email: str, my_skills: list[str], threshold: float = 0.5) -> list[JobPosting]:
        scored = [(match_score(job, my_skills), job) for job in self.store.all()]
        jobs = [job for score, job in sorted(scored, key=lambda pair: (-pair[0], pair[1].id)) if score >= threshold]
        if jobs:
            self.notifier.notify(email, jobs)
        return jobs

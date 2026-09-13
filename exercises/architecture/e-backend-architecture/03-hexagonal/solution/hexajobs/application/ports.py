"""Ports: what the application needs from the outside world. Owned here, implemented by adapters."""

from typing import Protocol

from hexajobs.domain.model import JobPosting


class JobFeed(Protocol):
    def fetch_jobs(self) -> list[JobPosting]: ...


class JobStore(Protocol):
    def save_all(self, jobs: list[JobPosting]) -> None: ...
    def all(self) -> list[JobPosting]: ...


class Notifier(Protocol):
    def notify(self, email: str, jobs: list[JobPosting]) -> None: ...

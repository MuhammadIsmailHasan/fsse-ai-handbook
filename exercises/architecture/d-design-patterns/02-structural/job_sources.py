"""Structural patterns for job sources. See README.md."""

from dataclasses import dataclass, field, replace
from typing import Callable, Protocol


@dataclass(frozen=True)
class Job:
    id: str
    title: str
    company: str
    salary_max: int | None = None


class JobSource(Protocol):
    def fetch(self) -> list[Job]: ...


class LegacyKarirFeed:
    """Provided: a third-party client we can't change. Its data uses Indonesian keys and text salaries."""

    def __init__(self, listings: list[dict]):
        self._listings = listings

    def get_listings(self) -> list[dict]:
        return [dict(item) for item in self._listings]


@dataclass
class RefreshResult:
    jobs: list[Job]
    counts: dict[str, int]
    failed: list[str] = field(default_factory=list)


# TODO: KarirFeedAdapter, CachedSource, RetryingSource, SalaryPrivacyProxy, JobBoards

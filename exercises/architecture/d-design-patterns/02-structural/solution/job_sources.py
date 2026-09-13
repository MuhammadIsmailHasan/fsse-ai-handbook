"""Structural patterns for job sources — reference solution."""

import re

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


class KarirFeedAdapter:
    """Adapter: makes LegacyKarirFeed look like a JobSource."""

    def __init__(self, feed: LegacyKarirFeed):
        self._feed = feed

    def fetch(self) -> list[Job]:
        return [self._convert(item) for item in self._feed.get_listings()]

    @staticmethod
    def _convert(item: dict) -> Job:
        salary = item.get("gaji", "")
        match = re.fullmatch(r"\s*Rp\s*([\d.]+)\s*", salary or "")
        return Job(
            id=f"karir-{item['lowongan_id']}",
            title=item["posisi"].strip(),
            company=item["perusahaan"].strip(),
            salary_max=int(match.group(1).replace(".", "")) if match else None,
        )


class CachedSource:
    """Decorator: adds caching without changing the wrapped source."""

    def __init__(self, inner: JobSource, ttl_seconds: float, clock: Callable[[], float]):
        self._inner, self._ttl, self._clock = inner, ttl_seconds, clock
        self._cached: list[Job] | None = None
        self._fetched_at = 0.0

    def fetch(self) -> list[Job]:
        now = self._clock()
        if self._cached is None or now - self._fetched_at >= self._ttl:
            self._cached = self._inner.fetch()
            self._fetched_at = now
        return list(self._cached)


class RetryingSource:
    """Decorator: retries transient connection failures."""

    def __init__(self, inner: JobSource, attempts: int = 3):
        self._inner, self._attempts = inner, attempts

    def fetch(self) -> list[Job]:
        for attempt in range(1, self._attempts + 1):
            try:
                return self._inner.fetch()
            except ConnectionError:
                if attempt == self._attempts:
                    raise
        raise AssertionError("unreachable")


class SalaryPrivacyProxy:
    """Protection proxy: same interface, controls what the caller may see."""

    def __init__(self, inner: JobSource, can_view_salaries: bool):
        self._inner, self._can_view = inner, can_view_salaries

    def fetch(self) -> list[Job]:
        jobs = self._inner.fetch()
        return jobs if self._can_view else [replace(job, salary_max=None) for job in jobs]


class JobBoards:
    """Facade: one simple call over many sources, with deduplication and error isolation."""

    def __init__(self, sources: dict[str, JobSource]):
        self._sources = sources

    def refresh(self) -> RefreshResult:
        jobs: dict[str, Job] = {}
        counts: dict[str, int] = {}
        failed: list[str] = []
        for name, source in self._sources.items():
            try:
                fetched = source.fetch()
            except Exception:
                failed.append(name)
                continue
            counts[name] = len(fetched)
            for job in fetched:
                jobs.setdefault(job.id, job)
        return RefreshResult(list(jobs.values()), counts, sorted(failed))

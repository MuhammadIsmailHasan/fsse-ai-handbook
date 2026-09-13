import pytest

from job_sources import (
    CachedSource,
    Job,
    JobBoards,
    KarirFeedAdapter,
    LegacyKarirFeed,
    RefreshResult,
    RetryingSource,
    SalaryPrivacyProxy,
)

LISTINGS = [
    {"lowongan_id": "K-12", "posisi": " Backend Engineer ", "perusahaan": "Kopi Data ", "gaji": "Rp 12.000.000"},
    {"lowongan_id": "K-13", "posisi": "Data Analyst", "perusahaan": "Awan Cloud", "gaji": "Negotiable"},
    {"lowongan_id": "K-14", "posisi": "QA", "perusahaan": "Batik Soft", "gaji": ""},
]


class StaticSource:
    def __init__(self, jobs):
        self.jobs, self.calls = jobs, 0

    def fetch(self):
        self.calls += 1
        return list(self.jobs)


class FlakySource:
    def __init__(self, failures, error=ConnectionError):
        self.failures, self.error, self.calls = failures, error, 0

    def fetch(self):
        self.calls += 1
        if self.calls <= self.failures:
            raise self.error("temporary")
        return [Job("flaky-1", "Dev", "Flaky Inc")]


def test_adapter_converts_legacy_format():
    assert KarirFeedAdapter(LegacyKarirFeed(LISTINGS)).fetch() == [
        Job("karir-K-12", "Backend Engineer", "Kopi Data", 12_000_000),
        Job("karir-K-13", "Data Analyst", "Awan Cloud", None),
        Job("karir-K-14", "QA", "Batik Soft", None),
    ]


def test_cached_source_respects_ttl_and_returns_copies():
    inner = StaticSource([Job("a", "Dev", "X")])
    now = [100.0]
    cached = CachedSource(inner, ttl_seconds=60, clock=lambda: now[0])
    first = cached.fetch()
    first.append(Job("mutated", "?", "?"))
    now[0] = 159.9
    assert cached.fetch() == [Job("a", "Dev", "X")] and inner.calls == 1
    now[0] = 160.0
    cached.fetch()
    assert inner.calls == 2


def test_retrying_source():
    flaky = FlakySource(failures=2)
    assert RetryingSource(flaky, attempts=3).fetch()[0].id == "flaky-1" and flaky.calls == 3
    always = FlakySource(failures=99)
    with pytest.raises(ConnectionError):
        RetryingSource(always, attempts=3).fetch()
    assert always.calls == 3
    not_transient = FlakySource(failures=1, error=ValueError)
    with pytest.raises(ValueError):
        RetryingSource(not_transient).fetch()
    assert not_transient.calls == 1, "only ConnectionError is retried"


def test_salary_privacy_proxy():
    inner = StaticSource([Job("a", "Dev", "X", 10_000_000)])
    assert SalaryPrivacyProxy(inner, can_view_salaries=True).fetch()[0].salary_max == 10_000_000
    assert SalaryPrivacyProxy(inner, can_view_salaries=False).fetch() == [Job("a", "Dev", "X", None)]
    assert inner.jobs[0].salary_max == 10_000_000, "don't modify the original jobs"


def test_wrappers_stack():
    flaky_feed = FlakySource(failures=1)
    now = [0.0]
    stacked = SalaryPrivacyProxy(CachedSource(RetryingSource(flaky_feed), 30, lambda: now[0]), can_view_salaries=False)
    assert stacked.fetch() == stacked.fetch() == [Job("flaky-1", "Dev", "Flaky Inc")]
    assert flaky_feed.calls == 2


def test_facade_dedupes_counts_and_isolates_failures():
    boards = JobBoards(
        {
            "karir": KarirFeedAdapter(LegacyKarirFeed(LISTINGS)),
            "broken": FlakySource(failures=99, error=RuntimeError),
            "partner": StaticSource([Job("karir-K-12", "Duplicate", "Kopi Data"), Job("p-1", "PM", "Lintas AI")]),
            "also-broken": FlakySource(failures=99),
        }
    )
    result = boards.refresh()
    assert isinstance(result, RefreshResult)
    assert [job.id for job in result.jobs] == ["karir-K-12", "karir-K-13", "karir-K-14", "p-1"]
    assert result.jobs[0].title == "Backend Engineer", "first source wins on duplicates"
    assert result.counts == {"karir": 3, "partner": 2}
    assert result.failed == ["also-broken", "broken"]

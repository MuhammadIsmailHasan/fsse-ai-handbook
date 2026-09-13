"""Tests for skills_gap.py. Don't edit this file."""

import dataclasses
import time
from collections import Counter

import pytest

from skills_gap import (
    JobListing,
    RecentlyViewed,
    best_matches,
    jobs_by_company,
    match_score,
    missing_skill_demand,
    missing_skills,
)

RAW = [
    {"id": 1, "title": "Backend Dev", "company": "Kopi Data", "required_skills": ["Python", " SQL ", "docker"]},
    {"id": 2, "title": "Data Analyst", "company": "Kopi Data", "required_skills": ["sql", "excel", ""]},
    {"id": 3, "title": "AI Engineer", "company": "Lintas AI", "required_skills": ["python", "llm", "docker"]},
    {"id": 4, "title": "Intern", "company": "Batik Soft", "required_skills": []},
]
MINE = {"python", " SQL", "React"}


@pytest.fixture
def jobs():
    return [JobListing.from_dict(item) for item in RAW]


def test_job_listing_is_frozen_slotted_dataclass(jobs):
    job = jobs[0]
    assert dataclasses.is_dataclass(job)
    assert job.required_skills == frozenset({"python", "sql", "docker"})
    with pytest.raises(dataclasses.FrozenInstanceError):
        job.title = "changed"
    assert not hasattr(job, "__dict__"), "Use slots=True"
    assert jobs[1].required_skills == frozenset({"sql", "excel"})


def test_match_score(jobs):
    assert match_score(jobs[0], MINE) == pytest.approx(2 / 3)
    assert match_score(jobs[2], MINE) == pytest.approx(1 / 3)
    assert match_score(jobs[3], MINE) == 1.0


def test_missing_skills(jobs):
    assert missing_skills(jobs[0], MINE) == ["docker"]
    assert missing_skills(jobs[2], MINE) == ["docker", "llm"]


def test_missing_skill_demand(jobs):
    assert missing_skill_demand(jobs, MINE) == Counter({"docker": 2, "excel": 1, "llm": 1})


def test_jobs_by_company(jobs):
    grouped = jobs_by_company(jobs)
    assert type(grouped) is dict
    assert [job.id for job in grouped["Kopi Data"]] == [1, 2]
    assert "Nobody" not in grouped


def test_best_matches(jobs):
    assert [job.id for job in best_matches(jobs, MINE, 3)] == [4, 1, 2]


def test_recently_viewed():
    recent = RecentlyViewed(limit=3)
    for job_id in [1, 2, 3, 2, 4]:
        recent.add(job_id)
    assert recent.items() == [4, 2, 3]


def test_membership_is_fast():
    big = JobListing(id=99, title="Big", company="X", required_skills=frozenset(f"skill{i}" for i in range(50_000)))
    my_skills = {f"skill{i}" for i in range(0, 100_000, 2)}
    started = time.perf_counter()
    for _ in range(5):
        missing_skills(big, my_skills)
    assert time.perf_counter() - started < 1.0, "Use set operations, not list scans"

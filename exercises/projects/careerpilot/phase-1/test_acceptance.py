"""CareerPilot Phase 1 — acceptance tests. Don't edit this file."""

import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from analyze import (
    filter_jobs,
    format_report,
    format_rupiah_number,
    jobs_by_city,
    load_jobs,
    salary_stats,
    top_skills,
)

HERE = Path(__file__).parent
DATA = HERE / "data" / "jobs.csv"


@pytest.fixture(scope="module")
def jobs():
    return load_jobs(str(DATA))


# ---- C1 · Load & clean -------------------------------------------------------


def test_skips_rows_without_title(jobs):
    assert len(jobs) == 24
    assert all(job["title"] for job in jobs)


def test_cleans_text_and_booleans(jobs):
    ml = next(job for job in jobs if job["id"] == "4")
    assert ml["title"] == "ML Engineer"
    assert ml["city"] == "Jakarta"
    assert ml["remote"] is True
    assert next(job for job in jobs if job["id"] == "7")["remote"] is True  # "1"
    assert next(job for job in jobs if job["id"] == "2")["remote"] is False


def test_parses_salaries_and_dates(jobs):
    first = jobs[0]
    assert (first["salary_min"], first["salary_max"]) == (9_000_000, 14_000_000)
    assert first["posted_on"] == date(2026, 9, 1)
    qa = next(job for job in jobs if job["id"] == "5")
    assert qa["salary_min"] is None and qa["salary_max"] is None
    assert next(job for job in jobs if job["id"] == "7")["posted_on"] is None


def test_normalizes_skills(jobs):
    assert next(job for job in jobs if job["id"] == "4")["skills"] == ["python", "pytorch", "docker"]
    assert next(job for job in jobs if job["id"] == "22")["skills"] == ["python", "flask", "sql"]


# ---- C2 · Analyze ------------------------------------------------------------


def test_filter_jobs(jobs):
    assert len(filter_jobs(jobs, city="jakarta")) == 13
    assert len(filter_jobs(jobs, remote=True)) == 9
    high = filter_jobs(jobs, city="Jakarta", remote=True, min_salary=20_000_000)
    assert [job["id"] for job in high] == ["4", "23"]
    assert len(filter_jobs(jobs)) == 24
    assert all(job["salary_max"] is not None for job in filter_jobs(jobs, min_salary=1))


def test_top_skills(jobs):
    assert top_skills(jobs, 3) == [("python", 15), ("sql", 9), ("react", 5)]
    assert top_skills(jobs, 5)[3:] == [("aws", 4), ("docker", 4)]  # tie → alphabetical
    assert top_skills([], 3) == []


def test_salary_stats(jobs):
    jakarta = filter_jobs(jobs, city="Jakarta")
    assert salary_stats(jakarta) == {
        "count": 12,
        "average_min": 11_875_000,
        "average_max": 18_208_333,
        "median_max": 19_000_000,
    }
    assert salary_stats(filter_jobs(jobs, city="Bandung"))["median_max"] == 13_000_000  # even count → middle average
    assert salary_stats([]) == {"count": 0, "average_min": 0, "average_max": 0, "median_max": 0}


def test_jobs_by_city(jobs):
    counts = jobs_by_city(jobs)
    assert list(counts.items()) == [
        ("Jakarta", 13),
        ("Bandung", 4),
        ("Surabaya", 3),
        ("Yogyakarta", 3),  # tie with Surabaya → alphabetical
        ("Remote Indonesia", 1),
    ]


# ---- C3 · Report & CLI -------------------------------------------------------


def test_format_rupiah_number():
    assert format_rupiah_number(9_611_111) == "9.611.111"
    assert format_rupiah_number(0) == "0"


def test_format_report(jobs):
    report = format_report(filter_jobs(jobs, city="Bandung"), top_n=2)
    assert report.splitlines() == [
        "CareerPilot · Job Market Report",
        "Jobs analyzed: 4",
        "",
        "Top skills:",
        "  1. python (3)",
        "  2. sql (3)",
        "",
        "Salary (IDR/month, jobs with salary data: 4):",
        "  Average range: 9.500.000 – 14.000.000",
        "  Median max: 13.000.000",
        "",
        "Jobs per city:",
        "  Bandung: 4",
    ]


def test_format_report_without_jobs():
    report = format_report([])
    assert "Jobs analyzed: 0" in report
    assert "No salary data" in report


def run_cli(*args):
    return subprocess.run([sys.executable, str(HERE / "cli.py"), *args], capture_output=True, text=True, cwd=HERE)


def test_cli_prints_filtered_report():
    result = run_cli(str(DATA), "--city", "bandung", "--top", "2")
    assert result.returncode == 0
    assert "Jobs analyzed: 4" in result.stdout
    assert "  2. sql (3)" in result.stdout


def test_cli_remote_and_min_salary_flags():
    result = run_cli(str(DATA), "--remote", "--min-salary", "20000000")
    assert result.returncode == 0
    assert "Jobs analyzed: 3" in result.stdout


def test_cli_missing_file():
    result = run_cli("nope.csv")
    assert result.returncode == 1
    assert "Error: file not found: nope.csv" in result.stderr

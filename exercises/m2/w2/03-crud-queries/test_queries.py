"""Loads seed.sql, runs each of your query files, and compares results. Don't edit this file."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

HERE = Path(__file__).parent


@pytest.fixture
def seeded(db, run_sql):
    run_sql(db, HERE / "seed.sql")
    return db


def run(seeded, query_sql, name):
    return query_sql(seeded, HERE / f"{name}.sql")


def test_q01_open_remote(seeded, query_sql):
    columns, rows = run(seeded, query_sql, "q01_open_remote")
    assert columns == ["title", "company"]
    assert rows == [
        ("AI Engineer", "Lintas AI"),
        ("Frontend Engineer", "Garuda Pay"),
        ("Full-Stack Developer", "Rempah Digital"),
        ("Junior Backend Engineer", "Nusantara Tech"),
        ("Junior Full-Stack Developer", "Batik Soft"),
        ("ML Engineer", "Lintas AI"),
    ]


def test_q02_salary_range(seeded, query_sql):
    columns, rows = run(seeded, query_sql, "q02_salary_range")
    assert columns == ["title", "salary_max"]
    assert rows == [
        ("AI Engineer", 21000000),
        ("Backend Engineer (Go)", 20000000),
        ("Full-Stack Developer", 15000000),
        ("Junior Backend Engineer", 14000000),
        ("Mobile Developer", 14000000),
        ("Frontend Developer", 13000000),
    ]


def test_q03_engineer_titles(seeded, query_sql):
    columns, rows = run(seeded, query_sql, "q03_engineer_titles")
    assert columns == ["title"]
    assert [r[0] for r in rows] == [
        "AI Engineer",
        "Backend Engineer (Go)",
        "DevOps Engineer",
        "Frontend Engineer",
        "Junior Backend Engineer",
        "Junior Data Engineer",
        "ML Engineer",
        "QA Engineer",
        "Site Reliability Engineer",
    ]


def test_q04_missing_salary(seeded, query_sql):
    columns, rows = run(seeded, query_sql, "q04_missing_salary")
    assert columns == ["title"]
    assert rows == [("Frontend Engineer",), ("QA Engineer",)]


def test_q05_count_per_city(seeded, query_sql):
    columns, rows = run(seeded, query_sql, "q05_count_per_city")
    assert columns == ["city", "total"]
    assert rows == [("Jakarta", 7), ("Bandung", 3), ("Surabaya", 2), ("Yogyakarta", 2)]


def test_q06_avg_salary_busy_cities(seeded, query_sql):
    columns, rows = run(seeded, query_sql, "q06_avg_salary_busy_cities")
    assert columns == ["city", "avg_max"]
    assert [(city, Decimal(value)) for city, value in rows] == [
        ("Jakarta", Decimal("18428571")),
        ("Bandung", Decimal("13333333")),
    ]


def test_q07_latest_three(seeded, query_sql):
    columns, rows = run(seeded, query_sql, "q07_latest_three")
    assert columns == ["title", "posted_on"]
    assert rows == [
        ("AI Engineer", date(2026, 9, 11)),
        ("ML Engineer", date(2026, 9, 10)),
        ("Frontend Engineer", date(2026, 9, 9)),
    ]


def test_q08_insert_returns_new_row(seeded, query_sql):
    columns, rows = run(seeded, query_sql, "q08_insert")
    assert columns == ["id", "title", "status"]
    (new_id, title, status), = rows
    assert isinstance(new_id, int) and title == "Platform Engineer" and status == "open"
    assert seeded.execute("SELECT COUNT(*) FROM job_listings").fetchone()[0] == 16


def test_q09_close_old(seeded, query_sql):
    columns, rows = run(seeded, query_sql, "q09_close_old")
    assert columns == ["title"]
    assert sorted(rows) == [("Data Analyst",), ("Mobile Developer",)]
    still_old_and_open = seeded.execute(
        "SELECT COUNT(*) FROM job_listings WHERE status = 'open' AND posted_on < '2026-08-29'"
    ).fetchone()[0]
    assert still_old_and_open == 0
    assert seeded.execute("SELECT COUNT(*) FROM job_listings WHERE status = 'closed'").fetchone()[0] == 5


def test_q10_delete_closed_without_salary(seeded, query_sql):
    columns, rows = run(seeded, query_sql, "q10_delete_closed_without_salary")
    assert columns == ["title"]
    assert rows == [("QA Engineer",)]
    assert seeded.execute("SELECT COUNT(*) FROM job_listings").fetchone()[0] == 14

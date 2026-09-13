"""Loads seed.sql and compares each query's result. Don't edit this file."""

from datetime import date
from pathlib import Path

import pytest

HERE = Path(__file__).parent

EXPECTED = {
    "q01_applications_with_names": (
        ["full_name", "company", "role_title"],
        [
            ("Ana Putri", "Kopi Data", "Data Analyst"),
            ("Ana Putri", "Lintas AI", "AI Engineer"),
            ("Ana Putri", "Nusantara Tech", "Backend Engineer"),
            ("Budi Santoso", "Garuda Pay", "QA Engineer"),
            ("Budi Santoso", "Kopi Data", "Data Analyst"),
            ("Budi Santoso", "Lintas AI", "AI Engineer"),
            ("Citra Lestari", "Garuda Pay", "Backend Engineer"),
            ("Citra Lestari", "Lintas AI", "ML Engineer"),
            ("Citra Lestari", "Nusantara Tech", "Frontend Developer"),
        ],
    ),
    "q02_users_without_applications": (["full_name"], [("Dewi Anggraini",)]),
    "q03_company_application_counts": (
        ["company", "applications"],
        [("Lintas AI", 3), ("Garuda Pay", 2), ("Kopi Data", 2), ("Nusantara Tech", 2), ("Batik Soft", 0)],
    ),
    "q04_offers_above_average": (["full_name", "company", "salary_offer"], [("Citra Lestari", "Lintas AI", 21000000)]),
    "q05_skills_for_ana": (["skill"], [("docker",), ("llm",), ("python",), ("sql",)]),
    "q06_skill_demand": (
        ["skill", "applications"],
        [("python", 7), ("sql", 4), ("llm", 3), ("docker", 2), ("react", 1), ("go", 0)],
    ),
    "q07_users_with_offer": (["full_name"], [("Ana Putri",), ("Budi Santoso",), ("Citra Lestari",)]),
    "q08_latest_application_per_user": (
        ["full_name", "role_title", "applied_on"],
        [
            ("Ana Putri", "Backend Engineer", date(2026, 8, 20)),
            ("Budi Santoso", "AI Engineer", date(2026, 9, 2)),
            ("Citra Lestari", "Frontend Developer", date(2026, 9, 5)),
        ],
    ),
    "q09_same_company_applicants": (
        ["company", "user_a", "user_b"],
        [
            ("Garuda Pay", "Budi Santoso", "Citra Lestari"),
            ("Kopi Data", "Ana Putri", "Budi Santoso"),
            ("Lintas AI", "Ana Putri", "Budi Santoso"),
            ("Lintas AI", "Ana Putri", "Citra Lestari"),
            ("Lintas AI", "Budi Santoso", "Citra Lestari"),
            ("Nusantara Tech", "Ana Putri", "Citra Lestari"),
        ],
    ),
    "q10_status_summary_cte": (
        ["full_name", "total", "active", "offers"],
        [("Ana Putri", 3, 1, 1), ("Budi Santoso", 3, 2, 1), ("Citra Lestari", 3, 1, 1)],
    ),
}


@pytest.fixture
def seeded(db, run_sql):
    run_sql(db, HERE / "seed.sql")
    return db


@pytest.mark.parametrize("name", EXPECTED)
def test_query(seeded, query_sql, name):
    expected_columns, expected_rows = EXPECTED[name]
    columns, rows = query_sql(seeded, HERE / f"{name}.sql")
    assert columns == expected_columns, f"{name}: column names/order"
    assert rows == expected_rows, f"{name}: rows"


def test_q07_uses_exists():
    sql = (HERE / "q07_users_with_offer.sql").read_text().upper()
    assert "EXISTS" in sql, "Use EXISTS for q07"


def test_q10_uses_cte():
    sql = (HERE / "q10_status_summary_cte.sql").read_text().upper()
    assert sql.lstrip().startswith("WITH") or "\nWITH " in sql, "Use a CTE (WITH …) for q10"

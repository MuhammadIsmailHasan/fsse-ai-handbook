"""Behavior tests for schema.sql: good data is accepted, bad data is rejected. Don't edit."""

from pathlib import Path

import psycopg
import pytest

SQL = Path(__file__).with_name("schema.sql")


@pytest.fixture
def conn(db, run_sql):
    run_sql(db, SQL)
    db.execute("INSERT INTO users (email, full_name) VALUES ('ana@mail.com', 'Ana')")
    db.execute("INSERT INTO companies (name) VALUES ('Kopi Data')")
    return db


def ids(conn):
    user_id = conn.execute("SELECT id FROM users WHERE email = 'ana@mail.com'").fetchone()[0]
    company_id = conn.execute("SELECT id FROM companies WHERE name = 'Kopi Data'").fetchone()[0]
    return user_id, company_id


def insert_application(conn, **overrides):
    user_id, company_id = ids(conn)
    values = {"user_id": user_id, "company_id": company_id, "role_title": "Data Analyst", **overrides}
    columns = ", ".join(values)
    placeholders = ", ".join(["%s"] * len(values))
    return conn.execute(
        f"INSERT INTO applications ({columns}) VALUES ({placeholders}) RETURNING id, status, created_at, updated_at",
        list(values.values()),
    ).fetchone()


def test_valid_application_gets_defaults(conn):
    _id, status, created_at, updated_at = insert_application(conn, applied_on="2026-09-13", salary_expectation=12_000_000)
    assert status == "applied"
    assert created_at is not None and updated_at is not None


def test_email_unique_ignoring_case(conn):
    with pytest.raises(psycopg.errors.UniqueViolation):
        conn.execute("INSERT INTO users (email, full_name) VALUES ('ANA@Mail.com', 'Ana Again')")


def test_required_user_fields(conn):
    with pytest.raises(psycopg.errors.NotNullViolation):
        conn.execute("INSERT INTO users (email) VALUES ('budi@mail.com')")


def test_company_name_unique(conn):
    with pytest.raises(psycopg.errors.UniqueViolation):
        conn.execute("INSERT INTO companies (name) VALUES ('Kopi Data')")


@pytest.mark.parametrize("status", ["wishlist", "applied", "interview", "offer", "rejected", "withdrawn"])
def test_allowed_statuses(conn, status):
    insert_application(conn, role_title=f"Role {status}", status=status)


@pytest.mark.parametrize("status", ["aplied", "Applied", "hired", ""])
def test_invalid_statuses(conn, status):
    with pytest.raises(psycopg.errors.CheckViolation):
        insert_application(conn, status=status)


def test_blank_role_title_rejected(conn):
    with pytest.raises((psycopg.errors.CheckViolation, psycopg.errors.NotNullViolation)):
        insert_application(conn, role_title="   ")


def test_negative_salary_rejected_but_null_allowed(conn):
    insert_application(conn, role_title="Analyst A", salary_expectation=None)
    with pytest.raises(psycopg.errors.CheckViolation):
        insert_application(conn, role_title="Analyst B", salary_expectation=-1)


def test_foreign_keys_enforced(conn):
    _user_id, company_id = ids(conn)
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        conn.execute(
            "INSERT INTO applications (user_id, company_id, role_title) VALUES (999999, %s, 'QA')", (company_id,)
        )


def test_no_duplicate_application_for_same_role(conn):
    insert_application(conn)
    with pytest.raises(psycopg.errors.UniqueViolation):
        insert_application(conn)
    insert_application(conn, role_title="Analytics Engineer")  # different role is fine


def test_timestamps_are_timestamptz(conn):
    types = dict(
        conn.execute(
            """SELECT table_name || '.' || column_name, data_type FROM information_schema.columns
               WHERE table_schema = current_schema() AND column_name IN ('created_at', 'updated_at')"""
        ).fetchall()
    )
    assert types and all(t == "timestamp with time zone" for t in types.values())
    assert {"users.created_at", "companies.created_at", "applications.created_at", "applications.updated_at"} <= set(types)

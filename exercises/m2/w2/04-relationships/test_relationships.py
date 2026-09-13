"""Behavior tests for relationships.sql. Don't edit this file."""

from pathlib import Path

import psycopg
import pytest

HERE = Path(__file__).parent


@pytest.fixture
def conn(db, run_sql):
    run_sql(db, HERE / "base.sql")
    run_sql(db, HERE / "relationships.sql")
    return db


def one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


@pytest.fixture
def data(conn):
    user = one(conn, "INSERT INTO users (email, full_name) VALUES ('ana@mail.com', 'Ana') RETURNING id")
    company = one(conn, "INSERT INTO companies (name) VALUES ('Kopi Data') RETURNING id")
    app = one(conn, "INSERT INTO applications (user_id, company_id, role_title) VALUES (%s, %s, 'Analyst') RETURNING id", (user, company))
    sql = one(conn, "INSERT INTO skills (name) VALUES ('sql') RETURNING id")
    conn.execute("INSERT INTO application_skills (application_id, skill_id, level) VALUES (%s, %s, 'required')", (app, sql))
    conn.execute("INSERT INTO interviews (application_id, scheduled_at) VALUES (%s, now())", (app,))
    conn.execute("INSERT INTO user_profiles (user_id, headline) VALUES (%s, 'Aspiring AI engineer')", (user,))
    return {"user": user, "company": company, "app": app, "skill": sql}


def count(conn, table):
    return one(conn, f"SELECT COUNT(*) FROM {table}")


def test_foreign_keys_reject_orphans(conn, data):
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        conn.execute("INSERT INTO applications (user_id, company_id, role_title) VALUES (999999, %s, 'X')", (data["company"],))
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        conn.execute("INSERT INTO interviews (application_id, scheduled_at) VALUES (999999, now())")


def test_many_to_many_no_duplicates(conn, data):
    with pytest.raises(psycopg.errors.UniqueViolation):
        conn.execute(
            "INSERT INTO application_skills (application_id, skill_id, level) VALUES (%s, %s, 'required')",
            (data["app"], data["skill"]),
        )


def test_skill_level_values(conn, data):
    python = one(conn, "INSERT INTO skills (name) VALUES ('python') RETURNING id")
    with pytest.raises(psycopg.errors.CheckViolation):
        conn.execute("INSERT INTO application_skills (application_id, skill_id, level) VALUES (%s, %s, 'expert')", (data["app"], python))


def test_one_profile_per_user(conn, data):
    with pytest.raises(psycopg.errors.UniqueViolation):
        conn.execute("INSERT INTO user_profiles (user_id, headline) VALUES (%s, 'Second')", (data["user"],))


def test_deleting_company_with_applications_is_restricted(conn, data):
    with pytest.raises((psycopg.errors.ForeignKeyViolation, psycopg.errors.RestrictViolation)):
        conn.execute("DELETE FROM companies WHERE id = %s", (data["company"],))


def test_deleting_linked_skill_is_restricted(conn, data):
    with pytest.raises((psycopg.errors.ForeignKeyViolation, psycopg.errors.RestrictViolation)):
        conn.execute("DELETE FROM skills WHERE id = %s", (data["skill"],))


def test_deleting_application_cascades(conn, data):
    conn.execute("DELETE FROM applications WHERE id = %s", (data["app"],))
    assert count(conn, "interviews") == 0
    assert count(conn, "application_skills") == 0
    assert count(conn, "skills") == 1  # the skill itself stays


def test_deleting_user_cascades_everything_they_own(conn, data):
    conn.execute("DELETE FROM users WHERE id = %s", (data["user"],))
    assert count(conn, "applications") == 0
    assert count(conn, "interviews") == 0
    assert count(conn, "application_skills") == 0
    assert count(conn, "user_profiles") == 0
    assert count(conn, "companies") == 1


def test_foreign_key_columns_are_indexed(conn):
    unindexed = conn.execute(
        """
        SELECT c.conrelid::regclass::text, a.attname
        FROM pg_constraint c
        JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = c.conkey[1]
        WHERE c.contype = 'f'
          AND c.connamespace = current_schema()::regnamespace
          AND NOT EXISTS (
              SELECT 1 FROM pg_index i
              WHERE i.indrelid = c.conrelid AND i.indkey[0] = c.conkey[1]
          )
        """
    ).fetchall()
    assert unindexed == [], f"Add indexes for foreign key columns: {unindexed}"

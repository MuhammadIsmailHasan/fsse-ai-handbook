"""Runs study_log.sql in a fresh schema and inspects the table. Don't edit this file."""

from pathlib import Path

import psycopg
import pytest

SQL = Path(__file__).with_name("study_log.sql")


@pytest.fixture
def conn(db, run_sql):
    run_sql(db, SQL)
    return db


def columns(conn):
    rows = conn.execute(
        """SELECT column_name, data_type, is_nullable, column_default, is_identity
           FROM information_schema.columns
           WHERE table_schema = current_schema() AND table_name = 'study_log'"""
    ).fetchall()
    return {name: {"type": t, "nullable": n == "YES", "default": d, "identity": i == "YES"} for name, t, n, d, i in rows}


def test_columns_and_types(conn):
    cols = columns(conn)
    assert set(cols) == {"id", "topic", "minutes", "studied_on", "mood", "created_at"}
    assert cols["id"]["type"] == "bigint" and cols["id"]["identity"]
    assert cols["topic"]["type"] == "text" and not cols["topic"]["nullable"]
    assert cols["minutes"]["type"] == "integer" and not cols["minutes"]["nullable"]
    assert cols["studied_on"]["type"] == "date" and not cols["studied_on"]["nullable"]
    assert cols["mood"]["nullable"]
    assert cols["created_at"]["type"] == "timestamp with time zone" and not cols["created_at"]["nullable"]


def test_primary_key(conn):
    pk = conn.execute(
        """SELECT kcu.column_name FROM information_schema.table_constraints tc
           JOIN information_schema.key_column_usage kcu USING (constraint_schema, constraint_name)
           WHERE tc.table_schema = current_schema() AND tc.table_name = 'study_log' AND tc.constraint_type = 'PRIMARY KEY'"""
    ).fetchall()
    assert pk == [("id",)]


def test_three_rows_with_defaults(conn):
    rows = conn.execute("SELECT studied_on = CURRENT_DATE, created_at IS NOT NULL FROM study_log").fetchall()
    assert len(rows) == 3
    assert all(today and created for today, created in rows)


@pytest.mark.parametrize("minutes", [0, 601, -5])
def test_minutes_range_enforced(conn, minutes):
    with pytest.raises(psycopg.errors.CheckViolation):
        conn.execute("INSERT INTO study_log (topic, minutes) VALUES ('x', %s)", (minutes,))


def test_mood_values_enforced(conn):
    conn.execute("INSERT INTO study_log (topic, minutes, mood) VALUES ('x', 10, 'great')")
    conn.execute("INSERT INTO study_log (topic, minutes, mood) VALUES ('x', 10, NULL)")
    with pytest.raises(psycopg.errors.CheckViolation):
        conn.execute("INSERT INTO study_log (topic, minutes, mood) VALUES ('x', 10, 'sleepy')")


def test_topic_required(conn):
    with pytest.raises(psycopg.errors.NotNullViolation):
        conn.execute("INSERT INTO study_log (minutes) VALUES (10)")


def test_id_is_generated_always(conn):
    with pytest.raises(psycopg.errors.GeneratedAlways):
        conn.execute("INSERT INTO study_log (id, topic, minutes) VALUES (999, 'x', 10)")

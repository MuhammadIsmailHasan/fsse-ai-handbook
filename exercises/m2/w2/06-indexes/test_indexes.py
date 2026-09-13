"""Checks query plans with your indexes. Don't edit this file."""

from pathlib import Path

import pytest

HERE = Path(__file__).parent


def load_queries():
    chunks = HERE.joinpath("queries.sql").read_text().split(";")
    queries = []
    for chunk in chunks:
        sql = "\n".join(line for line in chunk.splitlines() if not line.strip().startswith("--")).strip()
        if sql:
            queries.append(sql)
    return queries


QUERIES = load_queries()


def plan_nodes(plan, found=None):
    found = [] if found is None else found
    found.append((plan["Node Type"], plan.get("Relation Name")))
    for child in plan.get("Plans", []):
        plan_nodes(child, found)
    return found


@pytest.fixture
def indexed(db, run_sql):
    run_sql(db, HERE / "seed.sql")
    run_sql(db, HERE / "indexes.sql")
    db.execute("ANALYZE")
    return db


@pytest.mark.parametrize("number", range(1, len(QUERIES) + 1))
def test_query_avoids_sequential_scan(indexed, number):
    query = QUERIES[number - 1]
    plan = indexed.execute("EXPLAIN (FORMAT JSON) " + query).fetchone()[0][0]["Plan"]
    seq_scans = [relation for node, relation in plan_nodes(plan) if node == "Seq Scan"]
    assert not seq_scans, f"Q{number} still uses a Seq Scan on {seq_scans}:\n{query}"


def new_indexes(conn):
    return conn.execute(
        """SELECT i.indexrelid::regclass::text, i.indpred IS NOT NULL AS is_partial, t.relname
           FROM pg_index i
           JOIN pg_class t ON t.oid = i.indrelid
           WHERE t.relnamespace = current_schema()::regnamespace AND NOT i.indisprimary"""
    ).fetchall()


def test_at_most_four_indexes(indexed):
    indexes = new_indexes(indexed)
    assert len(indexes) <= 4, f"Too many indexes ({len(indexes)}): {[name for name, *_ in indexes]}"


def test_follow_up_index_is_partial(indexed):
    partial = [name for name, is_partial, table in new_indexes(indexed) if is_partial and table == "applications"]
    assert partial, "Make the follow-up index partial: CREATE INDEX … WHERE status IN ('applied', 'interview')"

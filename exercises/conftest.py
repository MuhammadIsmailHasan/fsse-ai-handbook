"""Shared pytest fixtures for all exercises.

`db` gives each test a PostgreSQL connection inside its own fresh schema, so tests
never interfere with each other and leave nothing behind.

Start the database first:  cd exercises && docker compose up -d
Override the connection:   DATABASE_URL=postgresql://user:pass@host:port/db
"""

import os
import uuid
from pathlib import Path

import pytest

DEFAULT_URL = f"postgresql://fsse:fsse@localhost:{os.environ.get('POSTGRES_PORT', '5491')}/fsse"


@pytest.fixture
def db():
    psycopg = pytest.importorskip("psycopg", reason="Run `uv sync` in exercises/ to install psycopg")
    url = os.environ.get("DATABASE_URL", DEFAULT_URL)
    try:
        conn = psycopg.connect(url, autocommit=True, connect_timeout=3)
    except psycopg.OperationalError as error:
        pytest.fail(
            "Can't connect to PostgreSQL. Start it with:  cd exercises && docker compose up -d\n"
            f"({error.__class__.__name__}: {str(error).strip().splitlines()[0]})",
            pytrace=False,
        )
    schema = f"t_{uuid.uuid4().hex[:12]}"
    conn.execute(f"CREATE SCHEMA {schema}")
    conn.execute(f"SET search_path TO {schema}")
    try:
        yield conn
    finally:
        conn.execute(f"DROP SCHEMA {schema} CASCADE")
        conn.close()


def run_sql_file(conn, path: Path) -> None:
    """Execute a .sql file. Fails with a clear message if the file is empty."""
    sql = Path(path).read_text().strip()
    if not sql or all(line.strip().startswith("--") or not line.strip() for line in sql.splitlines()):
        pytest.fail(f"{Path(path).name} has no SQL yet", pytrace=False)
    conn.execute(sql)


def query_file(conn, path: Path):
    """Run a SELECT from a .sql file and return (column_names, rows)."""
    sql = Path(path).read_text().strip().rstrip(";")
    if not sql or all(line.strip().startswith("--") or not line.strip() for line in sql.splitlines()):
        pytest.fail(f"{Path(path).name} has no query yet", pytrace=False)
    cursor = conn.execute(sql)
    columns = [column.name for column in cursor.description] if cursor.description else []
    return columns, cursor.fetchall()


@pytest.fixture
def run_sql():
    """Fixture form of run_sql_file, so tests don't import conftest."""
    return run_sql_file


@pytest.fixture
def query_sql():
    """Fixture form of query_file."""
    return query_file

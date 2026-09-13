"""Runs real Alembic upgrades/downgrades in a fresh PostgreSQL schema. Don't edit this file."""

from pathlib import Path

import pytest
from alembic.script import ScriptDirectory
from flask_migrate import downgrade, upgrade  # noqa: I001
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from app import MIGRATIONS_DIR, create_app
from models import db

HERE = Path(__file__).parent


@pytest.fixture
def app(pg_url):
    app = create_app(pg_url)
    with app.app_context():
        yield app
        db.session.remove()
        db.engine.dispose()


def end_session_transaction():
    # A SELECT through db.session keeps a transaction open that holds a lock on the table.
    # Alembic runs on another connection and would wait forever for that lock (ALTER TABLE).
    db.session.rollback()


def migrate_to(revision):
    end_session_transaction()
    upgrade(directory=MIGRATIONS_DIR, revision=revision)


def migrate_down_to(revision):
    end_session_transaction()
    downgrade(directory=MIGRATIONS_DIR, revision=revision)


def test_head_is_0002():
    script = ScriptDirectory(str(HERE / "migrations"))
    assert script.get_current_head() == "0002", "Create migration 0002 with down_revision = '0001'"


def columns():
    return {c["name"]: c for c in inspect(db.engine).get_columns("applications")}


def test_schema_after_upgrade(app):
    migrate_to("head")
    cols = columns()
    assert "salary_range" not in cols
    assert str(cols["salary_min"]["type"]) == "BIGINT" and cols["salary_min"]["nullable"]
    assert str(cols["salary_max"]["type"]) == "BIGINT" and cols["salary_max"]["nullable"]
    assert not cols["status"]["nullable"]
    assert "applied" in (cols["status"]["default"] or "")
    checks = {c["name"] for c in inspect(db.engine).get_check_constraints("applications")}
    assert "ck_applications_salary_range_valid" in checks


ROWS = [
    ("Kopi Data", "Data Analyst", "interview", "9000000-14000000"),
    ("Lintas AI", "AI Engineer", None, "15000000-25000000"),
    ("Batik Soft", "Frontend Dev", None, "negotiable"),
    ("Garuda Pay", "QA", "applied", None),
]


def insert_old_rows():
    for company, role, status, salary in ROWS:
        db.session.execute(
            text("INSERT INTO applications (company_name, role_title, status, salary_range) VALUES (:c, :r, :s, :sal)"),
            {"c": company, "r": role, "s": status, "sal": salary},
        )
    db.session.commit()


def test_backfill_keeps_data(app):
    migrate_to("0001")
    insert_old_rows()
    migrate_to("head")
    rows = db.session.execute(
        text("SELECT company_name, status, salary_min, salary_max FROM applications ORDER BY id")
    ).all()
    assert rows == [
        ("Kopi Data", "interview", 9_000_000, 14_000_000),
        ("Lintas AI", "applied", 15_000_000, 25_000_000),
        ("Batik Soft", "applied", None, None),
        ("Garuda Pay", "applied", None, None),
    ]


def test_new_rules_enforced(app):
    migrate_to("head")
    db.session.execute(text("INSERT INTO applications (company_name, role_title) VALUES ('X', 'Dev')"))
    db.session.commit()
    assert db.session.scalar(text("SELECT status FROM applications")) == "applied"
    with pytest.raises(IntegrityError):
        db.session.execute(text("INSERT INTO applications (company_name, role_title, salary_min, salary_max) VALUES ('Y', 'Dev', 20, 10)"))
        db.session.commit()
    db.session.rollback()


def test_downgrade_restores_old_shape_and_data(app):
    migrate_to("0001")
    insert_old_rows()
    migrate_to("head")
    migrate_down_to("0001")
    cols = columns()
    assert "salary_min" not in cols and "salary_max" not in cols
    assert cols["status"]["nullable"]
    rows = db.session.execute(text("SELECT company_name, salary_range FROM applications ORDER BY id")).all()
    assert rows == [
        ("Kopi Data", "9000000-14000000"),
        ("Lintas AI", "15000000-25000000"),
        ("Batik Soft", None),
        ("Garuda Pay", None),
    ]
    migrate_to("head")  # and it can go forward again

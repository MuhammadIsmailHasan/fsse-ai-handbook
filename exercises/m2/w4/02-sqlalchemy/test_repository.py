"""Tests for repository.py against real PostgreSQL. Don't edit this file."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import event, func, select

import repository as repo
from app import create_app
from models import Application, Company, db


@pytest.fixture
def app(pg_url):
    app = create_app(pg_url)
    with app.app_context():
        db.create_all()
        kopi, lintas = Company(name="Kopi Data"), Company(name="Lintas AI")
        db.session.add_all([kopi, lintas])
        db.session.flush()
        start = datetime(2026, 9, 1, tzinfo=timezone.utc)
        rows = [
            (7, kopi.id, "Data Analyst", "applied", 0),
            (7, lintas.id, "AI Engineer", "interview", 1),
            (7, kopi.id, "Analytics Engineer", "offer", 2),
            (7, lintas.id, "ML Engineer", "interview", 3),
            (8, kopi.id, "Data Analyst", "applied", 4),
        ]
        for user_id, company_id, role, status, day in rows:
            db.session.add(Application(user_id=user_id, company_id=company_id, role_title=role, status=status, created_at=start + timedelta(days=day)))
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def count_queries(app):
    statements = []

    def before(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(db.engine, "before_cursor_execute", before)
    yield statements
    event.remove(db.engine, "before_cursor_execute", before)


def test_no_legacy_query_api():
    source = Path(repo.__file__).read_text()
    assert ".query." not in source and ".query(" not in source, "Use select() instead of Model.query"


def test_get_for_user(app):
    own = db.session.scalars(select(Application).where(Application.user_id == 7)).first()
    other = db.session.scalars(select(Application).where(Application.user_id == 8)).first()
    assert repo.get_for_user(own.id, 7).id == own.id
    assert repo.get_for_user(other.id, 7) is None
    assert repo.get_for_user(999999, 7) is None


def test_list_applications_order_filter_pagination(app, count_queries):
    items, total = repo.list_applications(7, per_page=2, page=1)
    assert total == 4
    assert [a.role_title for a in items] == ["ML Engineer", "Analytics Engineer"]
    assert len(count_queries) == 2, f"Expected exactly 2 SQL statements, got {len(count_queries)}"

    items, total = repo.list_applications(7, per_page=2, page=2)
    assert [a.role_title for a in items] == ["AI Engineer", "Data Analyst"]

    items, total = repo.list_applications(7, statuses=["interview"])
    assert total == 2 and {a.role_title for a in items} == {"ML Engineer", "AI Engineer"}


def test_count_by_status(app):
    assert repo.count_by_status(7) == {"applied": 1, "interview": 2, "offer": 1}
    assert repo.count_by_status(99) == {}


def test_create_with_existing_company_case_insensitive(app):
    application = repo.create_application_with_company(7, "kopi DATA", "Backend Engineer")
    assert application.id is not None
    assert db.session.scalar(select(func.count()).select_from(Company)) == 2
    db.session.expire_all()
    assert db.session.get(Application, application.id).role_title == "Backend Engineer"


def test_create_with_new_company(app):
    application_id = repo.create_application_with_company(7, "Garuda Pay", "QA Engineer").id
    # Read the id BEFORE closing the session: after commit, objects are expired, and touching
    # an expired object whose session is gone raises DetachedInstanceError.
    db.session.remove()  # a brand-new session proves the rows were committed, not just pending
    saved = db.session.get(Application, application_id)
    assert db.session.get(Company, saved.company_id).name == "Garuda Pay"


def test_duplicate_rolls_back_everything(app):
    with pytest.raises(repo.DuplicateApplication):
        repo.create_application_with_company(7, "Kopi Data", "Data Analyst")
    # session is usable again, and nothing new was committed
    assert db.session.scalar(select(func.count()).select_from(Application)) == 5

    with pytest.raises(repo.DuplicateApplication):
        repo.create_application_with_company(8, "kopi data", "Data Analyst")
    assert db.session.scalar(select(func.count()).select_from(Company)) == 2

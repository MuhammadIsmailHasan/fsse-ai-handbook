"""Relationships, cascades and query counts on real PostgreSQL. Don't edit this file."""

from datetime import datetime, timedelta, timezone

import pytest
from flask import Flask
from sqlalchemy import event, func, select

from models import Application, Company, Interview, Skill, db
from queries import dashboard

NOW = datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def app(pg_url):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = pg_url
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def seeded(app):
    companies = [Company(name=f"Company {i}") for i in range(10)]
    skills = {name: Skill(name=name) for name in ["python", "sql", "react", "llm"]}
    db.session.add_all([*companies, *skills.values()])
    for i in range(30):
        application = Application(
            user_id=7,
            company=companies[i % 10],
            role_title=f"Role {i:02d}",
            created_at=NOW - timedelta(days=30 - i),
        )
        application.skills = [skills["sql"], skills["python"]] if i % 2 else [skills["react"]]
        application.interviews = [
            Interview(starts_at=NOW - timedelta(days=1)),       # past
            Interview(starts_at=NOW + timedelta(days=i + 2)),   # later upcoming
            Interview(starts_at=NOW + timedelta(days=i + 1)),   # next upcoming
        ]
        db.session.add(application)
    db.session.add(Application(user_id=8, company=companies[0], role_title="Other user"))
    db.session.commit()
    db.session.expunge_all()


def test_relationships_navigate_both_ways(seeded):
    company = db.session.scalars(select(Company).where(Company.name == "Company 1")).one()
    assert len(company.applications) == 3
    assert all(a.company is company for a in company.applications)
    python = db.session.scalars(select(Skill).where(Skill.name == "python")).one()
    assert len(python.applications) == 15
    application = company.applications[0]
    assert [i.starts_at for i in application.interviews] == sorted(i.starts_at for i in application.interviews)


def test_delete_orphan_and_cascade(seeded):
    application = db.session.scalars(select(Application).where(Application.role_title == "Role 00")).one()
    application.interviews.pop()          # removing from the collection deletes it
    db.session.commit()
    assert db.session.scalar(select(func.count()).select_from(Interview)) == 89
    db.session.delete(application)       # deleting the parent deletes owned children
    db.session.commit()
    assert db.session.scalar(select(func.count()).select_from(Interview)) == 87
    assert db.session.scalar(select(func.count()).select_from(Skill)) == 4   # shared data stays


def test_dashboard_output(seeded):
    rows = dashboard(7, NOW)
    assert len(rows) == 30
    first = rows[0]
    assert first["role_title"] == "Role 29" and first["company"] == "Company 9"
    assert first["skills"] == ["python", "sql"]
    assert first["next_interview"] == (NOW + timedelta(days=30)).isoformat()
    assert rows[-1]["skills"] == ["react"]
    assert all(row["id"] for row in rows)


def test_dashboard_runs_at_most_three_queries(seeded):
    statements = []

    def count(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(db.engine, "before_cursor_execute", count)
    try:
        dashboard(7, NOW)
    finally:
        event.remove(db.engine, "before_cursor_execute", count)
    assert len(statements) <= 3, f"{len(statements)} queries — this is the N+1 problem. Use eager loading."


def test_next_interview_none_when_no_upcoming(app):
    company = Company(name="Solo")
    application = Application(user_id=9, company=company, role_title="Dev")
    application.interviews = [Interview(starts_at=NOW - timedelta(hours=1))]
    db.session.add(application)
    db.session.commit()
    assert dashboard(9, NOW)[0]["next_interview"] is None

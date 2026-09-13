"""Creates your models in a fresh PostgreSQL schema and inspects the real tables. Don't edit."""

import pytest
from flask import Flask
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError

import models
from models import db


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
def insp(app):
    return inspect(db.engine)


def columns(insp, table):
    return {c["name"]: c for c in insp.get_columns(table)}


def test_nullability(insp):
    users, companies, apps = columns(insp, "users"), columns(insp, "companies"), columns(insp, "applications")
    assert not users["email"]["nullable"] and not users["full_name"]["nullable"]
    assert companies["website"]["nullable"] and not companies["name"]["nullable"]
    assert apps["salary_expectation"]["nullable"]
    for name in ("user_id", "company_id", "role_title", "status", "created_at", "updated_at"):
        assert not apps[name]["nullable"], f"applications.{name} must be NOT NULL"


def test_types(insp):
    apps = columns(insp, "applications")
    assert str(apps["salary_expectation"]["type"]) == "BIGINT"
    for table in ("users", "companies", "applications"):
        created = columns(insp, table)["created_at"]
        assert getattr(created["type"], "timezone", False), f"{table}.created_at must be timezone-aware"
        assert created["default"] and "now()" in created["default"]
    assert "applied" in (apps["status"]["default"] or "")


def test_named_constraints_and_indexes(insp):
    checks = {c["name"] for c in insp.get_check_constraints("applications")}
    assert {"ck_applications_role_title_not_blank", "ck_applications_salary_non_negative"} <= checks
    uniques = {u["name"] for u in insp.get_unique_constraints("applications")}
    assert "uq_applications_user_company_role" in uniques
    assert "uq_companies_name" in {u["name"] for u in insp.get_unique_constraints("companies")}
    indexes = {i["name"] for i in insp.get_indexes("applications")}
    assert "ix_applications_user_created" in indexes
    fks = {fk["name"]: fk for fk in insp.get_foreign_keys("applications")}
    assert fks["fk_applications_user_id_users"]["options"].get("ondelete") == "CASCADE"
    assert fks["fk_applications_company_id_companies"]["options"].get("ondelete") == "RESTRICT"
    assert insp.get_pk_constraint("applications")["name"] == "pk_applications"


def seed(app):
    user = models.User(email="Ana@Mail.com", full_name="Ana")
    company = models.Company(name="Kopi Data")
    db.session.add_all([user, company])
    db.session.flush()
    return user, company


def test_defaults_enum_repr_and_property(app):
    user, company = seed(app)
    application = models.Application(user_id=user.id, company_id=company.id, role_title="Data Analyst")
    db.session.add(application)
    db.session.commit()
    assert application.status == models.ApplicationStatus.APPLIED and application.is_active
    assert repr(application) == f"<Application id={application.id} 'Data Analyst' status=applied>"
    stored = db.session.execute(text("SELECT status FROM applications")).scalar()
    assert stored == "applied"


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO applications (user_id, company_id, role_title, status) VALUES (:u, :c, 'X', 'hired')",
        "INSERT INTO applications (user_id, company_id, role_title) VALUES (:u, :c, '   ')",
        "INSERT INTO applications (user_id, company_id, role_title, salary_expectation) VALUES (:u, :c, 'X', -1)",
        "INSERT INTO users (email, full_name) VALUES ('ANA@mail.com', 'Duplicate')",
    ],
)
def test_database_rejects_invalid_rows(app, sql):
    user, company = seed(app)
    db.session.commit()
    with pytest.raises(IntegrityError):
        db.session.execute(text(sql), {"u": user.id, "c": company.id})
        db.session.commit()
    db.session.rollback()


def test_server_default_status_for_raw_sql(app):
    user, company = seed(app)
    db.session.commit()
    db.session.execute(text("INSERT INTO applications (user_id, company_id, role_title) VALUES (:u, :c, 'Raw')"), {"u": user.id, "c": company.id})
    db.session.commit()
    assert db.session.scalar(select(models.Application.status)) == models.ApplicationStatus.APPLIED


def test_cascade_and_restrict(app):
    user, company = seed(app)
    db.session.add(models.Application(user_id=user.id, company_id=company.id, role_title="Analyst"))
    db.session.commit()
    with pytest.raises(IntegrityError):
        db.session.execute(text("DELETE FROM companies"))
        db.session.commit()
    db.session.rollback()
    db.session.execute(text("DELETE FROM users"))
    db.session.commit()
    assert db.session.scalar(text("SELECT count(*) FROM applications")) == 0

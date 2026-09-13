"""Fixtures for the CareerPilot Phase 2 acceptance tests. Don't edit this file.

Every test gets a fresh PostgreSQL schema, your Alembic migrations applied to it,
and a Flask test client.

Database URL (first match wins):
  TEST_DATABASE_URL  e.g. postgresql://careerpilot:careerpilot@localhost:5492/careerpilot_test
  default            postgresql://fsse:fsse@localhost:5491/fsse   (the handbook's exercise database)
"""

import os
import sys
import uuid
from itertools import count
from pathlib import Path

import pytest

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT))  # so `import careerpilot_api` works without installing the package

DEFAULT_URL = "postgresql://fsse:fsse@localhost:5491/fsse"
TEST_SECRET = "acceptance-tests-only-" + "x" * 32
PASSWORD = "correct-horse-battery"


@pytest.fixture
def schema_url():
    psycopg = pytest.importorskip("psycopg")
    url = os.environ.get("TEST_DATABASE_URL", DEFAULT_URL)
    try:
        conn = psycopg.connect(url, autocommit=True, connect_timeout=3)
    except psycopg.OperationalError as error:
        pytest.fail(f"Can't connect to PostgreSQL at {url!r}. Start it first. ({error.__class__.__name__})", pytrace=False)
    schema = f"cp_{uuid.uuid4().hex[:12]}"
    conn.execute(f"CREATE SCHEMA {schema}")
    base = url.replace("postgresql://", "postgresql+psycopg://", 1)
    separator = "&" if "?" in base else "?"
    try:
        yield f"{base}{separator}options=-csearch_path%3D{schema}", conn, schema
    finally:
        conn.execute(f"DROP SCHEMA {schema} CASCADE")
        conn.close()


@pytest.fixture
def app(schema_url):
    from flask_migrate import upgrade

    from careerpilot_api import create_app

    url, _, _ = schema_url
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": url, "JWT_SECRET_KEY": TEST_SECRET})
    with app.app_context():
        upgrade(directory=str(API_ROOT / "migrations"))
    yield app
    with app.app_context():
        app.extensions["sqlalchemy"].session.remove()
        app.extensions["sqlalchemy"].engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def raw_db(schema_url):
    """A psycopg connection whose search_path is the test schema (for checks behind the API)."""
    _, conn, schema = schema_url
    conn.execute(f"SET search_path TO {schema}")
    return conn


_emails = count(1)


def register_and_login(client, name="Siti Rahma"):
    email = f"user{next(_emails)}@careerpilot.test"
    response = client.post("/api/v1/auth/register", json={"email": email, "password": PASSWORD, "name": name})
    assert response.status_code == 201, response.get_json()
    token = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD}).get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth(client):
    return register_and_login(client)


@pytest.fixture
def other_auth(client):
    return register_and_login(client, name="Budi Santoso")


def make_company(client, headers, name="Kopi Data", **fields):
    response = client.post("/api/v1/companies", json={"name": name, **fields}, headers=headers)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def make_application(client, headers, company_id, role="Backend Engineer", **fields):
    response = client.post("/api/v1/applications", json={"company_id": company_id, "role": role, **fields}, headers=headers)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def move(client, headers, application_id, *statuses):
    data = None
    for status in statuses:
        response = client.post(f"/api/v1/applications/{application_id}/status", json={"status": status}, headers=headers)
        assert response.status_code == 200, (status, response.get_json())
        data = response.get_json()["data"]
    return data


@pytest.fixture
def helpers():
    class Helpers:
        company = staticmethod(make_company)
        application = staticmethod(make_application)
        move = staticmethod(move)
        register_and_login = staticmethod(register_and_login)

    return Helpers

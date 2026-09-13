"""Unit tests (no DB), API tests (PostgreSQL) and architecture rules. Don't edit this file."""

import ast
from datetime import datetime, timezone
from pathlib import Path

import pytest

from careerpilot import create_app
from careerpilot.errors import ApplicationNotFound, InvalidTransition, ValidationFailed
from careerpilot.models import Application, db
from careerpilot.services import ApplicationService

PACKAGE = Path(__file__).parent / "careerpilot"
FIXED_NOW = datetime(2026, 9, 13, 9, 0, tzinfo=timezone.utc)


# ---- Unit tests: the service with a fake repository, no database --------------


class FakeRepository:
    def __init__(self):
        self.items: dict[int, Application] = {}
        self.commits = 0
        self._next_id = 1

    def get_for_user(self, application_id, user_id):
        item = self.items.get(application_id)
        return item if item and item.user_id == user_id else None

    def list_for_user(self, user_id):
        return [a for a in self.items.values() if a.user_id == user_id]

    def add(self, application):
        application.id = self._next_id
        self.items[self._next_id] = application
        self._next_id += 1

    def commit(self):
        self.commits += 1


@pytest.fixture
def repo():
    return FakeRepository()


@pytest.fixture
def service(repo):
    return ApplicationService(repo, clock=lambda: FIXED_NOW)


def test_create(service, repo):
    application = service.create(7, {"company": " Kopi Data ", "role_title": "Analyst"})
    assert (application.company, application.status, application.user_id) == ("Kopi Data", "applied", 7)
    assert application.created_at == application.updated_at == FIXED_NOW
    assert repo.commits == 1


def test_create_validation_collects_all_fields(service, repo):
    with pytest.raises(ValidationFailed) as info:
        service.create(7, {"company": "   "})
    assert info.value.fields == {"company": "required", "role_title": "required"}
    assert repo.commits == 0


def test_change_status_flow(service, repo):
    application = service.create(7, {"company": "A", "role_title": "Dev"})
    service.change_status(7, application.id, "interview")
    updated = service.change_status(7, application.id, "offer")
    assert updated.status == "offer" and repo.commits == 3


@pytest.mark.parametrize("target", ["offer", "accepted", "applied", "hired"])
def test_invalid_transition(service, target):
    application = service.create(7, {"company": "A", "role_title": "Dev"})
    with pytest.raises(InvalidTransition):
        service.change_status(7, application.id, target)


def test_other_users_application_is_not_found(service):
    application = service.create(7, {"company": "A", "role_title": "Dev"})
    with pytest.raises(ApplicationNotFound):
        service.change_status(8, application.id, "interview")


# ---- API tests: routes + service + real repository on PostgreSQL -----------------------


@pytest.fixture
def client(pg_url):
    app = create_app(pg_url)
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


def headers(user_id=7):
    return {"X-User-Id": str(user_id)}


def test_api_create_list_and_status(client):
    created = client.post("/api/v1/applications", json={"company": "Kopi Data", "role_title": "Analyst"}, headers=headers())
    assert created.status_code == 201
    data = created.get_json()["data"]
    assert set(data) == {"id", "company", "role_title", "status"} and data["status"] == "applied"

    moved = client.post(f"/api/v1/applications/{data['id']}/status", json={"status": "interview"}, headers=headers())
    assert moved.status_code == 200 and moved.get_json()["data"]["status"] == "interview"

    listed = client.get("/api/v1/applications", headers=headers()).get_json()["data"]
    assert [a["id"] for a in listed] == [data["id"]]
    assert client.get("/api/v1/applications", headers=headers(8)).get_json()["data"] == []


def test_api_errors_come_from_domain_errors(client):
    assert client.get("/api/v1/applications").status_code == 401
    assert client.get("/api/v1/applications", headers={"X-User-Id": "abc"}).status_code == 401

    bad = client.post("/api/v1/applications", json={}, headers=headers())
    assert bad.status_code == 422 and bad.get_json()["error"]["fields"] == {"company": "required", "role_title": "required"}

    client.post("/api/v1/applications", json={"company": "X", "role_title": "Dev"}, headers=headers())
    duplicate = client.post("/api/v1/applications", json={"company": "X", "role_title": "Dev"}, headers=headers())
    assert duplicate.status_code == 409 and duplicate.get_json()["error"]["code"] == "duplicate_application"

    missing = client.post("/api/v1/applications/999/status", json={"status": "interview"}, headers=headers())
    assert missing.status_code == 404

    app_id = client.get("/api/v1/applications", headers=headers()).get_json()["data"][0]["id"]
    invalid = client.post(f"/api/v1/applications/{app_id}/status", json={"status": "accepted"}, headers=headers())
    assert invalid.status_code == 409 and invalid.get_json()["error"]["code"] == "invalid_transition"


# ---- Architecture rules: who may import what ---------------------------------------------


def imported_modules(filename):
    tree = ast.parse((PACKAGE / filename).read_text())
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module.split(".")[0] if node.level == 0 else node.module)
            names |= {alias.name for alias in node.names}
    return names


def test_services_are_framework_free():
    imports = imported_modules("services.py")
    assert not imports & {"flask", "sqlalchemy", "flask_sqlalchemy", "db", "select"}, f"services.py imports {imports}"


def test_routes_do_not_touch_the_database_directly():
    imports = imported_modules("routes.py")
    assert not imports & {"sqlalchemy", "flask_sqlalchemy", "db", "select"}, f"routes.py imports {imports}"

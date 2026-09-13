"""Reference integration tests for the applications API."""

import pytest

from app import create_app
from models import db

API = "/api/v1/applications"
KEY = {"X-API-Key": "test-key"}


@pytest.fixture
def app(pg_url):
    app = create_app(pg_url, api_key="test-key")
    # Push an app context only for setup/teardown. During the test, every request gets its OWN
    # context and session — like production — so uncommitted changes can't leak between requests.
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


def create(client, company="Kopi Data", role="Backend Engineer", headers=KEY):
    return client.post(API, json={"company": company, "role": role}, headers=headers)


def advance(client, application_id, *statuses):
    for status in statuses:
        response = client.patch(f"{API}/{application_id}/status", json={"status": status}, headers=KEY)
        assert response.status_code == 200, (status, response.get_json())


class TestCreate:
    def test_returns_201_with_saved_status_and_location(self, client):
        response = create(client, company="  Kopi Data ")
        assert response.status_code == 201
        data = response.get_json()["data"]
        assert data == {"id": data["id"], "company": "Kopi Data", "role": "Backend Engineer", "status": "saved"}
        assert response.headers["Location"].endswith(f"{API}/{data['id']}")

    def test_created_application_is_persisted(self, client):
        created = create(client).get_json()["data"]
        assert client.get(f"{API}/{created['id']}").get_json()["data"] == created

    @pytest.mark.parametrize("headers", [{}, {"X-API-Key": "wrong-key"}], ids=["missing", "wrong"])
    def test_requires_valid_api_key(self, client, headers):
        response = create(client, headers=headers)
        assert response.status_code == 401
        assert response.get_json() == {"error": {"code": "unauthorized"}}
        assert client.get(API).get_json()["data"] == []

    @pytest.mark.parametrize(
        "body",
        [{"company": "   ", "role": "Dev"}, {"company": "Kopi", "role": ""}, {"role": "Dev"}, {"company": 5, "role": "Dev"}, []],
    )
    def test_rejects_invalid_body(self, client, body):
        response = client.post(API, json=body, headers=KEY)
        assert response.status_code == 422
        assert response.get_json()["error"]["code"] == "validation_failed"


class TestRead:
    def test_list_is_ordered_by_id(self, client):
        ids = [create(client, company=name).get_json()["data"]["id"] for name in ("B", "A", "C")]
        assert [a["id"] for a in client.get(API).get_json()["data"]] == ids

    def test_filters_by_status(self, client):
        first = create(client, company="First").get_json()["data"]
        create(client, company="Second")
        advance(client, first["id"], "applied")
        applied = client.get(f"{API}?status=applied").get_json()["data"]
        assert [a["company"] for a in applied] == ["First"]

    def test_unknown_status_filter_is_422(self, client):
        assert client.get(f"{API}?status=ghosted").status_code == 422

    def test_missing_application_is_404(self, client):
        response = client.get(f"{API}/999999")
        assert response.status_code == 404
        assert response.get_json() == {"error": {"code": "not_found"}}


class TestChangeStatus:
    def test_happy_path_is_persisted(self, client):
        application_id = create(client).get_json()["data"]["id"]
        advance(client, application_id, "applied", "interview", "offer")
        assert client.get(f"{API}/{application_id}").get_json()["data"]["status"] == "offer"

    @pytest.mark.parametrize("path", [[], ["applied"], ["applied", "interview"]], ids=["saved", "applied", "interview"])
    def test_any_non_final_status_can_be_rejected(self, client, path):
        application_id = create(client).get_json()["data"]["id"]
        advance(client, application_id, *path, "rejected")

    @pytest.mark.parametrize(
        ("path", "target"),
        [([], "interview"), (["applied"], "offer"), (["applied", "interview", "offer"], "rejected"), ([], "saved")],
        ids=["saved-to-interview", "applied-to-offer", "offer-is-final", "saved-to-saved"],
    )
    def test_invalid_transition_is_409_and_unchanged(self, client, path, target):
        application_id = create(client).get_json()["data"]["id"]
        advance(client, application_id, *path)
        before = client.get(f"{API}/{application_id}").get_json()["data"]["status"]
        response = client.patch(f"{API}/{application_id}/status", json={"status": target}, headers=KEY)
        assert response.status_code == 409
        assert response.get_json()["error"]["code"] == "invalid_transition"
        assert client.get(f"{API}/{application_id}").get_json()["data"]["status"] == before

    def test_unknown_status_is_422(self, client):
        application_id = create(client).get_json()["data"]["id"]
        response = client.patch(f"{API}/{application_id}/status", json={"status": "ghosted"}, headers=KEY)
        assert response.status_code == 422

    def test_requires_api_key_and_existing_application(self, client):
        application_id = create(client).get_json()["data"]["id"]
        assert client.patch(f"{API}/{application_id}/status", json={"status": "applied"}).status_code == 401
        assert client.patch(f"{API}/999999/status", json={"status": "applied"}, headers=KEY).status_code == 404


class TestDelete:
    def test_delete_removes_application(self, client):
        application_id = create(client).get_json()["data"]["id"]
        assert client.delete(f"{API}/{application_id}", headers=KEY).status_code == 204
        assert client.get(f"{API}/{application_id}").status_code == 404

    def test_delete_requires_key_and_existing_application(self, client):
        application_id = create(client).get_json()["data"]["id"]
        assert client.delete(f"{API}/{application_id}").status_code == 401
        assert client.get(f"{API}/{application_id}").status_code == 200
        assert client.delete(f"{API}/999999", headers=KEY).status_code == 404

"""API tests on PostgreSQL. Don't edit this file."""

import pytest
from sqlalchemy import func, select

from app import create_app
from models import IdempotencyRecord, Note, db


@pytest.fixture
def app(pg_url):
    app = create_app(pg_url)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


def h(user=7, **extra):
    return {"X-User-Id": str(user), **extra}


def create(client, user=7, **fields):
    payload = {"title": "Interview prep", **fields}
    return client.post("/api/v1/notes", json=payload, headers=h(user))


def count(app, model):
    with app.app_context():
        return db.session.scalar(select(func.count()).select_from(model))


def test_create_defaults_status_and_location(client):
    response = create(client)
    assert response.status_code == 201
    note = response.get_json()["data"]
    assert note == {"id": note["id"], "title": "Interview prep", "body": None, "pinned": False}
    assert response.headers["Location"].endswith(f"/api/v1/notes/{note['id']}")
    assert client.get(f"/api/v1/notes/{note['id']}", headers=h()).get_json()["data"] == note


def test_auth_and_ownership(client):
    assert client.post("/api/v1/notes", json={"title": "x"}).status_code == 401
    note_id = create(client).get_json()["data"]["id"]
    for method in ("get", "put", "patch", "delete"):
        response = getattr(client, method)(f"/api/v1/notes/{note_id}", json={"title": "hack"}, headers=h(8))
        assert response.status_code == 404, f"{method.upper()} on another user's note must be 404"


def test_create_rejects_unknown_read_only_and_invalid_fields(client):
    response = client.post(
        "/api/v1/notes",
        json={"title": "  ", "user_id": 8, "id": 99, "pinnned": True, "pinned": "yes", "body": 5},
        headers=h(),
    )
    assert response.status_code == 422
    fields = response.get_json()["error"]["fields"]
    assert fields["user_id"] == "read-only field" and fields["id"] == "read-only field"
    assert fields["pinnned"] == "unknown field"
    assert {"title", "pinned", "body"} <= set(fields)


def test_invalid_json(client):
    response = client.post("/api/v1/notes", data="nope", content_type="application/json", headers=h())
    assert response.status_code == 400 and response.get_json()["error"]["code"] == "invalid_json"


def test_title_length_limit(client):
    assert create(client, title="x" * 121).status_code == 422
    assert create(client, title="x" * 120).status_code == 201


def test_put_replaces_everything(client):
    note_id = create(client, body="old body", pinned=True).get_json()["data"]["id"]
    response = client.put(f"/api/v1/notes/{note_id}", json={"title": "Replaced"}, headers=h())
    assert response.status_code == 200
    assert response.get_json()["data"] == {"id": note_id, "title": "Replaced", "body": None, "pinned": False}
    assert client.put(f"/api/v1/notes/{note_id}", json={"body": "no title"}, headers=h()).status_code == 422


def test_patch_merge_semantics(client):
    note_id = create(client, body="keep me", pinned=True).get_json()["data"]["id"]
    title_only = client.patch(f"/api/v1/notes/{note_id}", json={"title": "Renamed"}, headers=h()).get_json()["data"]
    assert title_only == {"id": note_id, "title": "Renamed", "body": "keep me", "pinned": True}

    cleared = client.patch(f"/api/v1/notes/{note_id}", json={"body": None}, headers=h()).get_json()["data"]
    assert cleared["body"] is None and cleared["title"] == "Renamed" and cleared["pinned"] is True

    null_title = client.patch(f"/api/v1/notes/{note_id}", json={"title": None}, headers=h())
    assert null_title.status_code == 422 and null_title.get_json()["error"]["fields"]["title"] == "cannot be null"

    empty = client.patch(f"/api/v1/notes/{note_id}", json={}, headers=h())
    assert empty.status_code == 422 and empty.get_json()["error"]["code"] == "no_fields"


def test_delete_then_404(client, app):
    note_id = create(client).get_json()["data"]["id"]
    first = client.delete(f"/api/v1/notes/{note_id}", headers=h())
    assert first.status_code == 204 and first.data == b""
    assert client.delete(f"/api/v1/notes/{note_id}", headers=h()).status_code == 404
    assert client.get(f"/api/v1/notes/{note_id}", headers=h()).status_code == 404
    assert count(app, Note) == 0


def test_idempotent_retry_returns_same_response(client, app):
    headers = h(**{"Idempotency-Key": "a1b2c3"})
    first = client.post("/api/v1/notes", json={"title": "Pay once"}, headers=headers)
    retry = client.post("/api/v1/notes", json={"title": "Pay once"}, headers=headers)
    assert first.status_code == retry.status_code == 201
    assert retry.get_json() == first.get_json()
    assert retry.headers["Location"] == first.headers["Location"]
    assert count(app, Note) == 1 and count(app, IdempotencyRecord) == 1


def test_idempotency_key_reused_with_different_body(client, app):
    headers = h(**{"Idempotency-Key": "same-key"})
    client.post("/api/v1/notes", json={"title": "First"}, headers=headers)
    response = client.post("/api/v1/notes", json={"title": "Different"}, headers=headers)
    assert response.status_code == 422 and response.get_json()["error"]["code"] == "idempotency_key_reused"
    assert count(app, Note) == 1


def test_idempotency_keys_are_per_user(client, app):
    client.post("/api/v1/notes", json={"title": "A"}, headers=h(7, **{"Idempotency-Key": "k"}))
    other = client.post("/api/v1/notes", json={"title": "A"}, headers=h(8, **{"Idempotency-Key": "k"}))
    assert other.status_code == 201
    assert count(app, Note) == 2


def test_failed_validation_does_not_store_key(client, app):
    headers = h(**{"Idempotency-Key": "bad-then-good"})
    assert client.post("/api/v1/notes", json={"title": ""}, headers=headers).status_code == 422
    assert client.post("/api/v1/notes", json={"title": "Now valid"}, headers=headers).status_code == 201

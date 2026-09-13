"""CRUD + error handling tests on PostgreSQL. Don't edit this file."""

import logging
import re

import pytest

from app import create_app
from models import Company, Job, db


@pytest.fixture
def app(pg_url):
    app = create_app(pg_url)
    app.config["PROPAGATE_EXCEPTIONS"] = False

    @app.get("/boom")
    def boom():
        raise RuntimeError("password=hunter2 in a secret stack trace")

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


def create(client, **fields):
    return client.post("/api/v1/companies", json={"name": "Kopi Data", **fields})


def test_create_read_list(client):
    response = create(client, website="https://kopidata.id")
    assert response.status_code == 201
    company = response.get_json()["data"]
    assert company == {"id": company["id"], "name": "Kopi Data", "website": "https://kopidata.id"}
    assert response.headers["Location"].endswith(f"/api/v1/companies/{company['id']}")
    assert client.get(f"/api/v1/companies/{company['id']}").get_json()["data"] == company
    client.post("/api/v1/companies", json={"name": "awan cloud"})
    client.post("/api/v1/companies", json={"name": "Batik Soft"})
    names = [c["name"] for c in client.get("/api/v1/companies").get_json()["data"]]
    assert names == ["awan cloud", "Batik Soft", "Kopi Data"]
    assert [c["name"] for c in client.get("/api/v1/companies?q=SOFT").get_json()["data"]] == ["Batik Soft"]
    assert client.get("/api/v1/companies?q=nothing").get_json()["data"] == []


def test_validation_errors(client):
    response = client.post("/api/v1/companies", json={"name": " ", "website": "http://insecure.example", "size": 10})
    assert response.status_code == 422
    error = response.get_json()["error"]
    assert error["code"] == "validation_failed"
    assert {"name", "website", "size"} <= set(error["fields"])
    bad_json = client.post("/api/v1/companies", data="nope", content_type="application/json")
    assert bad_json.status_code == 422 and "body" in bad_json.get_json()["error"]["fields"]


def test_duplicate_name_is_409_and_session_recovers(client):
    create(client)
    duplicate = client.post("/api/v1/companies", json={"name": "KOPI DATA"})
    assert duplicate.status_code == 409 and duplicate.get_json()["error"]["code"] == "company_exists"
    assert create(client, name="Another").status_code == 201, "session must be usable after the IntegrityError"


def test_patch_and_duplicate_on_patch(client):
    first = create(client).get_json()["data"]
    second = client.post("/api/v1/companies", json={"name": "Lintas AI"}).get_json()["data"]
    patched = client.patch(f"/api/v1/companies/{first['id']}", json={"website": "https://new.example"})
    assert patched.status_code == 200 and patched.get_json()["data"]["name"] == "Kopi Data"
    conflict = client.patch(f"/api/v1/companies/{second['id']}", json={"name": "kopi data"})
    assert conflict.status_code == 409 and conflict.get_json()["error"]["code"] == "company_exists"


def test_delete_and_in_use(client, app):
    unused = create(client, name="Unused").get_json()["data"]
    used = create(client, name="Used").get_json()["data"]
    with app.app_context():
        db.session.add(Job(company_id=used["id"], title="Backend Engineer"))
        db.session.commit()
    assert client.delete(f"/api/v1/companies/{unused['id']}").status_code == 204
    assert client.delete(f"/api/v1/companies/{unused['id']}").status_code == 404
    in_use = client.delete(f"/api/v1/companies/{used['id']}")
    assert in_use.status_code == 409 and in_use.get_json()["error"]["code"] == "company_in_use"
    assert client.get(f"/api/v1/companies/{used['id']}").status_code == 200


def test_not_found_codes(client):
    response = client.get("/api/v1/companies/12345")
    assert response.status_code == 404 and response.get_json()["error"]["code"] == "company_not_found"
    route = client.get("/api/v1/nothing-here")
    assert route.status_code == 404 and route.get_json()["error"]["code"] == "not_found"
    method = client.put("/api/v1/companies")
    assert method.status_code == 405 and method.get_json()["error"]["code"] == "method_not_allowed"


def test_request_id_generated_and_echoed(client):
    generated = client.get("/api/v1/companies/999")
    rid = generated.headers["X-Request-ID"]
    assert re.fullmatch(r"[0-9a-f]{32}", rid)
    assert generated.get_json()["error"]["request_id"] == rid

    echoed = client.get("/api/v1/companies/999", headers={"X-Request-ID": "trace-abc-123"})
    assert echoed.headers["X-Request-ID"] == "trace-abc-123"
    assert echoed.get_json()["error"]["request_id"] == "trace-abc-123"

    # Untrusted ids (spaces, markup, too long) must be replaced, never copied into headers or logs.
    for unsafe in ["bad id <script>", "x" * 100]:
        response = client.get("/api/v1/companies", headers={"X-Request-ID": unsafe})
        assert response.headers["X-Request-ID"] != unsafe
        assert re.fullmatch(r"[0-9a-f]{32}", response.headers["X-Request-ID"])


def test_unexpected_error_is_generic_and_logged(client, caplog):
    with caplog.at_level(logging.ERROR):
        response = client.get("/boom", headers={"X-Request-ID": "req-500-test"})
    assert response.status_code == 500
    assert response.get_json() == {
        "error": {"code": "internal_error", "message": "Something went wrong", "request_id": "req-500-test"}
    }
    assert "hunter2" not in response.get_data(as_text=True)
    assert any("req-500-test" in record.getMessage() for record in caplog.records), "log the request id"
    assert any(record.exc_info for record in caplog.records), "use logger.exception so the traceback is logged"

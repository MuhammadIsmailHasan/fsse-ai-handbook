"""C1 · Platform — app factory, health, errors, request ids, docs, fail-fast settings."""

import pytest
from fastapi.testclient import TestClient


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_every_response_has_a_request_id(client):
    r = client.get("/health")
    assert r.headers["X-Request-ID"]


def test_safe_incoming_request_id_is_reused(client):
    r = client.get("/health", headers={"X-Request-ID": "trace-123.abc_X"})
    assert r.headers["X-Request-ID"] == "trace-123.abc_X"


def test_unsafe_incoming_request_id_is_replaced(client):
    r = client.get("/health", headers={"X-Request-ID": "bad id with spaces\t<script>"})
    assert r.headers["X-Request-ID"] != "bad id with spaces\t<script>"
    assert r.headers["X-Request-ID"]


def test_two_requests_get_different_generated_ids(client):
    a = client.get("/health").headers["X-Request-ID"]
    b = client.get("/health").headers["X-Request-ID"]
    assert a != b


def test_unknown_route_is_json_404(client):
    r = client.get("/nope")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "not_found"
    assert r.headers["X-Request-ID"]


def test_wrong_method_is_json_405(client):
    r = client.get("/v1/match")
    assert r.status_code == 405
    assert r.json()["error"]["code"] == "method_not_allowed"


def test_openapi_documents_both_endpoints(client):
    spec = client.get("/openapi.json").json()
    assert "/v1/match" in spec["paths"]
    assert "/v1/feedback" in spec["paths"]
    assert "post" in spec["paths"]["/v1/match"]


def test_docs_page_is_served(client):
    assert client.get("/docs").status_code == 200


def test_missing_secret_fails_fast(monkeypatch):
    from careerpilot_ai import create_app

    monkeypatch.delenv("JWT_SECRET", raising=False)
    with pytest.raises(Exception):
        create_app({})


def test_short_secret_fails_fast():
    from careerpilot_ai import create_app

    with pytest.raises(Exception):
        create_app({"jwt_secret": "too-short"})


def test_secret_can_come_from_the_environment(monkeypatch):
    from careerpilot_ai import create_app

    monkeypatch.setenv("JWT_SECRET", "e" * 40)
    app = create_app({})
    assert TestClient(app).get("/health").status_code == 200


def test_override_beats_the_environment(monkeypatch):
    from careerpilot_ai import create_app
    from p3_support import CV, JOB, TEST_SECRET, make_token

    monkeypatch.setenv("JWT_SECRET", "e" * 40)
    client = TestClient(create_app({"jwt_secret": TEST_SECRET}))
    headers = {"Authorization": f"Bearer {make_token()}"}
    assert client.post("/v1/match", json={"cv_text": CV, "job_text": JOB}, headers=headers).status_code == 200

"""C1 · Platform and C2 · Auth."""

import pytest
from fastapi.testclient import TestClient

from p_support import TEST_SECRET, bearer, make_token


def test_health_needs_no_token(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json() == {"status": "ok"}


def test_every_response_has_a_request_id_and_safe_ids_are_reused(client):
    assert client.get("/health").headers["X-Request-ID"]
    assert client.get("/health", headers={"X-Request-ID": "trace-1.a_B"}).headers["X-Request-ID"] == "trace-1.a_B"
    bad = client.get("/health", headers={"X-Request-ID": "bad id <script>"}).headers["X-Request-ID"]
    assert bad and bad != "bad id <script>"


def test_unknown_route_and_wrong_method_are_json_errors(client):
    r = client.get("/nope")
    assert r.status_code == 404 and r.json()["error"]["code"] == "not_found"
    r = client.get("/v1/chat")
    assert r.status_code == 405 and r.json()["error"]["code"] == "method_not_allowed"


def test_openapi_lists_the_main_endpoints(client):
    paths = client.get("/openapi.json").json()["paths"]
    for path in ("/v1/chat", "/v1/articles", "/v1/feedback", "/v1/admin/conversations", "/v1/admin/handoffs"):
        assert path in paths
    assert client.get("/docs").status_code == 200


def test_missing_or_short_secret_fails_fast(monkeypatch):
    from supportdesk_api import create_app

    monkeypatch.delenv("JWT_SECRET", raising=False)
    with pytest.raises(Exception):
        create_app({})
    with pytest.raises(Exception):
        create_app({"jwt_secret": "too-short"})


def test_secret_from_the_environment_and_override_wins(monkeypatch):
    from supportdesk_api import create_app

    monkeypatch.setenv("JWT_SECRET", "e" * 40)
    env_client = TestClient(create_app({}))
    assert env_client.get("/health").status_code == 200
    app = create_app({"jwt_secret": TEST_SECRET})
    other = TestClient(app)
    # the env secret must NOT be accepted when an override is given
    r = other.post("/v1/chat", json={"message": "hi"}, headers=bearer(make_token(secret="e" * 40)))
    assert r.status_code == 401


BODY = {"message": "How long do refunds take?"}


def test_chat_needs_a_valid_token(client):
    assert client.post("/v1/chat", json=BODY).status_code == 401
    assert client.post("/v1/chat", json=BODY).json()["error"]["code"] == "unauthorized"
    assert client.post("/v1/chat", json=BODY, headers={"Authorization": f"Token {make_token()}"}).status_code == 401
    assert client.post("/v1/chat", json=BODY, headers=bearer("not.a.jwt")).status_code == 401
    assert client.post("/v1/chat", json=BODY, headers=bearer(make_token(secret="o" * 40))).status_code == 401
    assert client.post("/v1/chat", json=BODY, headers=bearer(make_token(expires_in=-5))).status_code == 401
    assert client.post("/v1/chat", json=BODY, headers=bearer(make_token(sub=None))).status_code == 401


def test_alg_none_token_is_rejected(client):
    import base64
    import json

    def b64(d):
        return base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b"=").decode()

    forged = f"{b64({'alg': 'none', 'typ': 'JWT'})}.{b64({'sub': 'x', 'role': 'admin', 'exp': 9999999999})}."
    assert client.post("/v1/chat", json=BODY, headers=bearer(forged)).status_code == 401
    assert client.get("/v1/admin/handoffs", headers=bearer(forged)).status_code == 401


def test_auth_is_checked_before_the_body(client):
    assert client.post("/v1/chat", json={}).status_code == 401


ADMIN_ROUTES = [
    ("GET", "/v1/articles"),
    ("POST", "/v1/articles"),
    ("DELETE", "/v1/articles/refund-policy"),
    ("GET", "/v1/admin/conversations"),
    ("GET", "/v1/admin/conversations/c-1"),
    ("GET", "/v1/admin/handoffs"),
    ("POST", "/v1/admin/handoffs/h-1/resolve"),
]


@pytest.mark.parametrize(("method", "path"), ADMIN_ROUTES)
def test_admin_routes_reject_a_customer_with_403(client, customer, method, path):
    r = client.request(method, path, json={} if method == "POST" else None, headers=customer)
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "forbidden"


@pytest.mark.parametrize(("method", "path"), ADMIN_ROUTES)
def test_admin_routes_reject_anonymous_with_401(client, method, path):
    r = client.request(method, path, json={} if method == "POST" else None)
    assert r.status_code == 401

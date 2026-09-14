"""Smoke tests for a running RevoShop deployment. Set REVOSHOP_URL to run them (see README.md)."""

import json
import os
import statistics
import time
import urllib.error
import urllib.request
import uuid
from urllib.parse import urlsplit

import pytest

BASE_URL = os.environ.get("REVOSHOP_URL", "").rstrip("/")
pytestmark = pytest.mark.skipif(not BASE_URL, reason="set REVOSHOP_URL to smoke-test a deployment")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def request(method: str, path: str, *, body: dict | None = None, token: str | None = None, follow_redirects: bool = True, base: str | None = None):
    headers = {"Accept": "application/json", "User-Agent": "revoshop-smoke/1.0"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request((base or BASE_URL) + path, data=data, headers=headers, method=method)
    opener = urllib.request.build_opener() if follow_redirects else urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=10) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as error:
        return error.code, dict(error.headers), error.read()


def as_json(raw: bytes):
    try:
        return json.loads(raw)
    except ValueError:
        pytest.fail(f"expected JSON, got: {raw[:200]!r}")


def test_health_reports_database_up():
    status, _, raw = request("GET", "/api/v1/health")
    body = as_json(raw)
    assert status == 200, body
    assert body.get("data", {}).get("database") == "up"


def test_api_docs_load():
    status, _, raw = request("GET", "/docs/swagger-ui")
    assert status == 200
    assert b"swagger" in raw.lower()


def test_unknown_route_returns_json_404():
    status, headers, raw = request("GET", f"/api/v1/does-not-exist-{uuid.uuid4().hex[:6]}")
    assert status == 404
    assert "application/json" in headers.get("Content-Type", "")
    as_json(raw)


def test_not_served_by_the_development_server():
    _, headers, _ = request("GET", "/api/v1/health")
    assert "werkzeug" not in headers.get("Server", "").lower(), "use gunicorn (behind a reverse proxy), not `flask run`"


@pytest.mark.skipif(os.environ.get("REVOSHOP_SKIP_WRITES") == "1", reason="REVOSHOP_SKIP_WRITES=1")
def test_register_login_and_profile():
    suffix = uuid.uuid4().hex[:10]
    user = {"username": f"smoke_{suffix}", "email": f"smoke_{suffix}@example.com", "password": "Smoke-test-pass-123", "role": "buyer"}
    status, _, raw = request("POST", "/api/v1/users/", body=user)
    assert status == 201, as_json(raw)

    status, _, raw = request("POST", "/api/v1/auth/login", body={"email": user["email"], "password": user["password"]})
    body = as_json(raw)
    assert status == 200, body
    token = body.get("access_token")
    assert token, "login response must include access_token"

    status, _, raw = request("GET", "/api/v1/users/me", token=token)
    body = as_json(raw)
    assert status == 200, body
    assert body["data"]["email"] == user["email"]


def test_product_list_is_paginated():
    status, _, raw = request("GET", "/api/v1/products/?page=1&limit=5")
    body = as_json(raw)
    assert status == 200, body
    assert isinstance(body.get("data"), list)
    assert {"page", "limit", "total_items", "total_pages"} <= set(body.get("pagination", {}))


def test_health_latency():
    durations = []
    for _ in range(10):
        started = time.perf_counter()
        status, _, _ = request("GET", "/api/v1/health")
        durations.append(time.perf_counter() - started)
        assert status == 200
    p95 = statistics.quantiles(durations, n=20)[-1]
    assert p95 < 0.8, f"health p95 {p95:.3f}s"


@pytest.mark.skipif(os.environ.get("REVOSHOP_EXPECT_HTTPS") != "1", reason="set REVOSHOP_EXPECT_HTTPS=1 for TLS checks")
def test_https_is_enforced():
    parts = urlsplit(BASE_URL)
    assert parts.scheme == "https", "REVOSHOP_URL should be https:// in production"
    _, headers, _ = request("GET", "/api/v1/health")
    assert "max-age=" in headers.get("Strict-Transport-Security", ""), "send an HSTS header from the proxy"
    status, headers, _ = request("GET", "/api/v1/health", follow_redirects=False, base=f"http://{parts.netloc}")
    assert status in (301, 308) and headers.get("Location", "").startswith("https://")

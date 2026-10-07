"""C2 · Auth — the same Bearer JWT as the Phase 2 API (HS256, `sub` + `exp`), checked by signature."""

import pytest

from p3_support import CV, JOB, make_token

BODY = {"cv_text": CV, "job_text": JOB}
ENDPOINTS = ["/v1/match", "/v1/feedback"]


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize("path", ENDPOINTS)
def test_no_header_is_401(client, path):
    r = client.post(path, json=BODY)
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "unauthorized"


@pytest.mark.parametrize("path", ENDPOINTS)
def test_wrong_scheme_is_401(client, path):
    r = client.post(path, json=BODY, headers={"Authorization": f"Token {make_token()}"})
    assert r.status_code == 401


@pytest.mark.parametrize("path", ENDPOINTS)
def test_garbage_token_is_401(client, path):
    assert client.post(path, json=BODY, headers=bearer("not.a.jwt")).status_code == 401


@pytest.mark.parametrize("path", ENDPOINTS)
def test_wrong_signature_is_401(client, path):
    token = make_token(secret="another-secret-" + "y" * 32)
    assert client.post(path, json=BODY, headers=bearer(token)).status_code == 401


@pytest.mark.parametrize("path", ENDPOINTS)
def test_expired_token_is_401(client, path):
    token = make_token(expires_in=-10)
    assert client.post(path, json=BODY, headers=bearer(token)).status_code == 401


@pytest.mark.parametrize("path", ENDPOINTS)
def test_token_without_sub_is_401(client, path):
    assert client.post(path, json=BODY, headers=bearer(make_token(sub=None))).status_code == 401


def test_alg_none_token_is_rejected(client):
    import base64
    import json

    def b64(data):
        return base64.urlsafe_b64encode(json.dumps(data).encode()).rstrip(b"=").decode()

    forged = f"{b64({'alg': 'none', 'typ': 'JWT'})}.{b64({'sub': 'attacker', 'exp': 9999999999})}."
    assert client.post("/v1/match", json=BODY, headers=bearer(forged)).status_code == 401


def test_valid_token_is_accepted(client, auth):
    assert client.post("/v1/match", json=BODY, headers=auth).status_code == 200


def test_health_needs_no_token(client):
    assert client.get("/health").status_code == 200


def test_auth_is_checked_before_the_body(client):
    # An unauthenticated caller must not learn anything about validation rules.
    r = client.post("/v1/match", json={})
    assert r.status_code == 401

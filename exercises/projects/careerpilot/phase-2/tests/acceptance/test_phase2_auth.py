"""C2 · Authentication. Don't edit."""

import time

import jwt
import pytest

PASSWORD = "correct-horse-battery"  # same values as tests/conftest.py
TEST_SECRET = "acceptance-tests-only-" + "x" * 32


def test_register_returns_public_profile(client):
    response = client.post("/api/v1/auth/register", json={"email": "  Siti@Example.COM ", "password": PASSWORD, "name": " Siti "})
    assert response.status_code == 201
    data = response.get_json()["data"]
    assert data == {"id": data["id"], "email": "siti@example.com", "name": "Siti"}


@pytest.mark.parametrize(
    ("body", "field"),
    [
        ({"email": "not-an-email", "password": PASSWORD, "name": "A"}, "email"),
        ({"email": "a@b.id", "password": "short", "name": "A"}, "password"),
        ({"email": "a@b.id", "password": PASSWORD, "name": "   "}, "name"),
        ({"email": "a@b.id", "password": PASSWORD}, "name"),
    ],
)
def test_register_validation(client, body, field):
    response = client.post("/api/v1/auth/register", json=body)
    assert response.status_code == 422
    error = response.get_json()["error"]
    assert error["code"] == "validation_failed" and field in error["fields"]


def test_register_rejects_non_json_body(client):
    response = client.post("/api/v1/auth/register", data="email=a@b.id", content_type="application/x-www-form-urlencoded")
    assert response.status_code == 422 and response.get_json()["error"]["code"] == "validation_failed"


def test_duplicate_email_is_case_insensitive(client):
    client.post("/api/v1/auth/register", json={"email": "budi@example.com", "password": PASSWORD, "name": "Budi"})
    response = client.post("/api/v1/auth/register", json={"email": "BUDI@example.com", "password": PASSWORD, "name": "Budi 2"})
    assert response.status_code == 409 and response.get_json()["error"]["code"] == "email_taken"


def test_password_is_not_stored_in_plain_text(client, raw_db):
    client.post("/api/v1/auth/register", json={"email": "plain@example.com", "password": PASSWORD, "name": "P"})
    tables = [row[0] for row in raw_db.execute("SELECT tablename FROM pg_tables WHERE schemaname = current_schema()")]
    for table in tables:
        hits = raw_db.execute(f'SELECT count(*) FROM "{table}" t WHERE t::text LIKE %s', (f"%{PASSWORD}%",)).fetchone()[0]
        assert hits == 0, f"plain-text password found in table {table}"


def test_login_and_me(client):
    client.post("/api/v1/auth/register", json={"email": "dewi@example.com", "password": PASSWORD, "name": "Dewi"})
    response = client.post("/api/v1/auth/login", json={"email": "DEWI@example.com", "password": PASSWORD})
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["token_type"] == "Bearer" and isinstance(data["expires_in"], int) and data["expires_in"] > 0
    me = client.get("/api/v1/me", headers={"Authorization": f"Bearer {data['access_token']}"})
    assert me.status_code == 200 and me.get_json()["data"]["email"] == "dewi@example.com"


def test_login_failures_look_the_same(client):
    client.post("/api/v1/auth/register", json={"email": "eka@example.com", "password": PASSWORD, "name": "Eka"})
    wrong_password = client.post("/api/v1/auth/login", json={"email": "eka@example.com", "password": "wrong-password"})
    unknown_email = client.post("/api/v1/auth/login", json={"email": "nobody@example.com", "password": PASSWORD})
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.get_json() == unknown_email.get_json()
    assert wrong_password.get_json()["error"]["code"] == "invalid_credentials"


def forged(secret, **claims):
    now = int(time.time())
    payload = {"sub": "1", "iat": now - 7200, "nbf": now - 7200, "exp": now + 3600, "jti": "forged", "type": "access", "fresh": False}
    return jwt.encode({**payload, **claims}, secret, algorithm="HS256")


@pytest.mark.parametrize(
    "header",
    [
        None,
        "Bearer not-a-jwt",
        "Token abc",
        "Bearer " + forged("some-other-secret-" + "y" * 32),
        "Bearer " + forged(TEST_SECRET, exp=int(time.time()) - 60),
    ],
    ids=["missing", "garbage", "wrong-scheme", "wrong-signature", "expired"],
)
def test_protected_endpoints_return_json_401(client, header):
    headers = {"Authorization": header} if header else {}
    response = client.get("/api/v1/me", headers=headers)
    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "unauthorized"

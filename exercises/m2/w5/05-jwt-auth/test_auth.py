"""Authentication tests on PostgreSQL. Don't edit this file."""

from datetime import timedelta

import pytest
from flask_jwt_extended import create_access_token, decode_token
from sqlalchemy import select

from app import create_app
from models import RevokedToken, User, db

PASSWORD = "correct-horse-battery"


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


def register(client, email="Ana@Mail.com", password=PASSWORD, full_name="Ana Putri"):
    return client.post("/api/v1/auth/register", json={"email": email, "password": password, "full_name": full_name})


def login(client, email="ana@mail.com", password=PASSWORD):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def test_register_hashes_password_and_hides_it(client, app):
    response = register(client)
    assert response.status_code == 201
    user = response.get_json()["data"]
    assert user == {"id": user["id"], "email": "ana@mail.com", "full_name": "Ana Putri", "role": "user"}
    with app.app_context():
        stored = db.session.scalars(select(User)).one().password_hash
    assert PASSWORD not in stored and len(stored) > 40


@pytest.mark.parametrize(
    ("payload", "field"),
    [
        ({"email": "not-an-email", "password": PASSWORD, "full_name": "A"}, "email"),
        ({"email": "a@mail.com", "password": "short", "full_name": "A"}, "password"),
        ({"email": "a@mail.com", "password": PASSWORD, "full_name": ""}, "full_name"),
    ],
)
def test_register_validation(client, payload, field):
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422 and field in response.get_json()["error"]["fields"]


def test_register_duplicate_email_any_case(client):
    register(client)
    response = register(client, email="ANA@mail.com")
    assert response.status_code == 409 and response.get_json()["error"]["code"] == "email_taken"


def test_login_success_and_token_contents(client, app):
    user_id = register(client).get_json()["data"]["id"]
    response = login(client, email=" ANA@mail.com ")
    assert response.status_code == 200
    body = response.get_json()
    assert body["token_type"] == "Bearer" and body["expires_in"] == 900
    with app.app_context():
        claims = decode_token(body["access_token"])
    assert claims["sub"] == str(user_id) and claims["role"] == "user" and claims["type"] == "access"


def test_login_errors_are_identical(client):
    register(client)
    wrong_password = login(client, password="wrong-password-123")
    unknown_email = login(client, email="nobody@mail.com")
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.get_json() == unknown_email.get_json()
    assert wrong_password.get_json()["error"]["code"] == "invalid_credentials"


def test_me_with_access_token(client):
    register(client)
    tokens = login(client).get_json()
    me = client.get("/api/v1/auth/me", headers=bearer(tokens["access_token"]))
    assert me.status_code == 200 and me.get_json()["data"]["email"] == "ana@mail.com"


def code(response):
    return response.status_code, response.get_json()["error"]["code"]


def test_token_errors(client, app):
    user_id = register(client).get_json()["data"]["id"]
    tokens = login(client).get_json()
    assert code(client.get("/api/v1/auth/me")) == (401, "token_missing")
    assert code(client.get("/api/v1/auth/me", headers=bearer("abc.def.ghi"))) == (401, "token_invalid")
    assert code(client.get("/api/v1/auth/me", headers=bearer(tokens["refresh_token"]))) == (401, "token_invalid")
    with app.app_context():
        expired = create_access_token(identity=str(user_id), expires_delta=timedelta(seconds=-5))
    assert code(client.get("/api/v1/auth/me", headers=bearer(expired))) == (401, "token_expired")


def test_refresh_only_with_refresh_token(client):
    register(client)
    tokens = login(client).get_json()
    assert code(client.post("/api/v1/auth/refresh", headers=bearer(tokens["access_token"]))) == (401, "token_invalid")
    refreshed = client.post("/api/v1/auth/refresh", headers=bearer(tokens["refresh_token"]))
    assert refreshed.status_code == 200
    assert client.get("/api/v1/auth/me", headers=bearer(refreshed.get_json()["access_token"])).status_code == 200


def test_logout_revokes_access_token(client, app):
    register(client)
    access = login(client).get_json()["access_token"]
    assert client.post("/api/v1/auth/logout", headers=bearer(access)).status_code == 204
    assert code(client.get("/api/v1/auth/me", headers=bearer(access))) == (401, "token_revoked")
    with app.app_context():
        record = db.session.scalars(select(RevokedToken)).one()
    assert record.token_type == "access" and record.expires_at is not None
    assert client.get("/api/v1/auth/me", headers=bearer(login(client).get_json()["access_token"])).status_code == 200


def test_logout_refresh_revokes_refresh_token(client):
    register(client)
    refresh = login(client).get_json()["refresh_token"]
    assert client.post("/api/v1/auth/logout-refresh", headers=bearer(refresh)).status_code == 204
    assert code(client.post("/api/v1/auth/refresh", headers=bearer(refresh))) == (401, "token_revoked")


def test_deleted_user_token_rejected(client, app):
    register(client)
    access = login(client).get_json()["access_token"]
    with app.app_context():
        db.session.delete(db.session.scalars(select(User)).one())
        db.session.commit()
    assert code(client.get("/api/v1/auth/me", headers=bearer(access))) == (401, "user_not_found")

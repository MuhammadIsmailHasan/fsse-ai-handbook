from fastapi.testclient import TestClient

from app import app, get_current_user

client = TestClient(app)


def test_no_token_is_401():
    assert client.get("/me").status_code == 401


def test_bad_format_is_401():
    assert client.get("/me", headers={"Authorization": "tok-ismail"}).status_code == 401


def test_unknown_token_is_401():
    r = client.get("/me", headers={"Authorization": "Bearer nope"})
    assert r.status_code == 401


def test_valid_token_returns_user():
    r = client.get("/me", headers={"Authorization": "Bearer tok-ismail"})
    assert r.status_code == 200
    assert r.json() == {"id": 1, "name": "Ismail"}


def test_dependency_override_injects_fake_user():
    app.dependency_overrides[get_current_user] = lambda: {"id": 99, "name": "Fake"}
    try:
        r = client.get("/me")  # no real token needed now
        assert r.status_code == 200
        assert r.json() == {"id": 99, "name": "Fake"}
    finally:
        app.dependency_overrides.clear()

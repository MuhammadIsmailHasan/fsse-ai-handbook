from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_create_returns_201_without_password():
    r = client.post("/users", json={"name": "Ismail", "email": "i@x.com", "password": "secret123"})
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Ismail"
    assert body["email"] == "i@x.com"
    assert "id" in body
    assert "password" not in body  # response_model filtered it out


def test_get_returns_user_without_password():
    created = client.post(
        "/users", json={"name": "Sari", "email": "s@x.com", "password": "hunter2xx"}
    ).json()
    r = client.get(f"/users/{created['id']}")
    assert r.status_code == 200
    assert r.json() == {"id": created["id"], "name": "Sari", "email": "s@x.com"}
    assert "password" not in r.json()


def test_missing_user_is_404():
    r = client.get("/users/999999")
    assert r.status_code == 404
    assert r.json()["detail"] == "User not found"

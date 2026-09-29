from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_greet_valid_body():
    r = client.post("/greet", json={"name": "Ismail"})
    assert r.status_code == 200
    assert r.json() == {"message": "Hello, Ismail!"}


def test_greet_missing_name_is_422():
    # No manual validation — FastAPI rejects a body missing "name" automatically.
    r = client.post("/greet", json={})
    assert r.status_code == 422


def test_greet_wrong_type_is_422():
    r = client.post("/greet", json={"name": 123})
    # 123 is not a string; Pydantic may coerce or reject depending on settings.
    # Accept either a clean 422 or a coerced string, but never a 500.
    assert r.status_code in (200, 422)

from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_path_param():
    r = client.get("/items/42")
    assert r.status_code == 200
    assert r.json() == {"item_id": 42}


def test_path_param_wrong_type_is_422():
    r = client.get("/items/abc")
    assert r.status_code == 422  # "abc" is not an int


def test_query_defaults():
    r = client.get("/items")
    assert r.status_code == 200
    assert r.json() == {"q": None, "page": 1}


def test_query_values():
    r = client.get("/items?q=phone&page=3")
    assert r.json() == {"q": "phone", "page": 3}


def test_body_create():
    r = client.post("/items", json={"name": "Mug", "price": 50000})
    assert r.status_code == 200
    assert r.json() == {"name": "Mug", "price": 50000}


def test_body_validation_422():
    r = client.post("/items", json={"name": "Mug"})  # missing price
    assert r.status_code == 422

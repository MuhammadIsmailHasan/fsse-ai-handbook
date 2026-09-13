"""Tests for the jobboard package. Don't edit this file."""

import pytest

from jobboard import create_app
from jobboard.config import TestingConfig


@pytest.fixture
def app():
    app = create_app(TestingConfig)

    @app.get("/boom")
    def boom():
        raise RuntimeError("secret internal detail")

    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_factory_config_and_blueprints(app):
    assert app.config["TESTING"] is True
    assert {"jobs", "health"} <= set(app.blueprints)


def test_each_app_has_its_own_store():
    first, second = create_app(TestingConfig), create_app(TestingConfig)
    first.test_client().post("/api/v1/jobs", json={"title": "X", "company": "Y"})
    assert len(second.extensions["jobs_store"]) == 4


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200 and response.get_json() == {"status": "ok"}


def test_list_jobs(client):
    body = client.get("/api/v1/jobs").get_json()
    assert body["meta"]["total"] == 4 and len(body["data"]) == 4


def test_list_filters(client):
    jakarta = client.get("/api/v1/jobs?city=JAKARTA").get_json()["data"]
    assert [job["id"] for job in jakarta] == [1, 3]
    remote = client.get("/api/v1/jobs?remote=true").get_json()["data"]
    assert [job["id"] for job in remote] == [1, 4]
    both = client.get("/api/v1/jobs?city=jakarta&remote=false").get_json()["data"]
    assert [job["id"] for job in both] == [3]


def test_invalid_filter(client):
    response = client.get("/api/v1/jobs?remote=maybe")
    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "invalid_filter"


def test_get_job_and_not_found(client):
    assert client.get("/api/v1/jobs/2").get_json()["data"]["company"] == "Kopi Data"
    response = client.get("/api/v1/jobs/99")
    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "job_not_found"


def test_create_job(client):
    response = client.post("/api/v1/jobs", json={"title": " ML Engineer ", "company": "Lintas AI", "remote": True})
    assert response.status_code == 201
    job = response.get_json()["data"]
    assert job == {"id": 5, "title": "ML Engineer", "company": "Lintas AI", "city": None, "remote": True}
    assert response.headers["Location"].endswith("/api/v1/jobs/5")
    assert client.get("/api/v1/jobs/5").status_code == 200


def test_create_validation(client):
    response = client.post("/api/v1/jobs", json={"title": "  ", "remote": "yes"})
    assert response.status_code == 422
    error = response.get_json()["error"]
    assert error["code"] == "validation_failed"
    assert error["fields"] == {"title": "required", "company": "required", "remote": "must be a boolean"}


def test_create_invalid_json(client):
    response = client.post("/api/v1/jobs", data="not json", content_type="application/json")
    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "invalid_json"
    assert client.post("/api/v1/jobs", json=["a", "list"]).status_code == 400


def test_json_errors_for_404_405_500(client):
    not_found = client.get("/nope")
    assert not_found.status_code == 404 and not_found.get_json()["error"]["code"] == "not_found"
    wrong_method = client.delete("/api/v1/jobs")
    assert wrong_method.status_code == 405 and wrong_method.get_json()["error"]["code"] == "method_not_allowed"


def test_unexpected_error_hides_details():
    app = create_app(TestingConfig)
    app.config["PROPAGATE_EXCEPTIONS"] = False

    @app.get("/boom")
    def boom():
        raise RuntimeError("secret internal detail")

    response = app.test_client().get("/boom")
    assert response.status_code == 500
    assert response.get_json() == {"error": {"code": "internal_error", "message": "Something went wrong"}}

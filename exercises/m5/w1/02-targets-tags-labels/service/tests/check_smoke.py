"""Provided: the tests the `test` build target runs (no database needed)."""

from app import create_app


def test_liveness():
    app = create_app("sqlite://")
    response = app.test_client().get("/health/live")
    assert response.status_code == 200

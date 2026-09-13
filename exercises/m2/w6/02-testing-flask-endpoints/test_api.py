"""YOUR integration tests for api.py (real Flask app + PostgreSQL).

Run your tests:         uv run pytest m2/w6/02-testing-flask-endpoints/test_api.py -v
Check against mutants:  uv run pytest m2/w6/02-testing-flask-endpoints/test_grader.py -v

The shared `pg_url` fixture (exercises/conftest.py) gives you a database URL in a fresh schema.
"""

import pytest

from app import create_app
from models import db


@pytest.fixture
def client(pg_url):
    app = create_app(pg_url, api_key="test-key")
    with app.app_context():
        db.create_all()
        yield app.test_client()  # ⚠️ Is keeping the app context open during requests a good idea? (see README)
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


def test_list_starts_empty(client):
    assert client.get("/api/v1/applications").status_code == 200

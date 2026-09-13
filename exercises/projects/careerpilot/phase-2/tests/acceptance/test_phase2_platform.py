"""C1 · Platform: app factory, migrations, health checks, error format, request ids. Don't edit."""

from pathlib import Path

from flask_migrate import downgrade

API_ROOT = Path(__file__).resolve().parents[2]


def test_health_endpoints(client):
    live = client.get("/health/live")
    assert live.status_code == 200 and live.get_json() == {"status": "ok"}
    ready = client.get("/health/ready")
    assert ready.status_code == 200 and ready.get_json() == {"status": "ok", "checks": {"database": "ok"}}


def test_every_response_has_a_request_id(client):
    generated = client.get("/health/live").headers.get("X-Request-ID")
    assert generated and len(generated) >= 16
    assert client.get("/health/live", headers={"X-Request-ID": "trace-abc_123"}).headers["X-Request-ID"] == "trace-abc_123"
    assert client.get("/nope").headers.get("X-Request-ID")


def test_unknown_routes_and_methods_return_json_errors(client):
    missing = client.get("/api/v1/does-not-exist")
    assert missing.status_code == 404 and missing.get_json()["error"]["code"] == "not_found"
    assert isinstance(missing.get_json()["error"]["message"], str)
    wrong_method = client.put("/health/live")
    assert wrong_method.status_code == 405 and wrong_method.get_json()["error"]["code"] == "method_not_allowed"


def test_migrations_downgrade_to_base_cleanly(app, raw_db):
    with app.app_context():
        app.extensions["sqlalchemy"].session.remove()
        downgrade(directory=str(API_ROOT / "migrations"), revision="base")
    tables = {row[0] for row in raw_db.execute("SELECT tablename FROM pg_tables WHERE schemaname = current_schema()")}
    assert tables <= {"alembic_version"}, f"downgrade left tables behind: {tables}"

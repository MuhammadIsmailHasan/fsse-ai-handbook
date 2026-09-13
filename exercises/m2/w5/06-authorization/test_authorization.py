"""Permission matrix tests on PostgreSQL. Don't edit this file."""

import pytest
from flask_jwt_extended import create_access_token

from app import create_app
from models import Application, User, db


@pytest.fixture
def app(pg_url):
    app = create_app(pg_url)
    # Push an app context ONLY for setup/teardown. If a context stayed pushed during the test,
    # every request would reuse one SQLAlchemy session and its cached objects (stale roles!).
    with app.app_context():
        db.create_all()
        users = {
            "ana": User(email="ana@mail.com", role="user"),
            "budi": User(email="budi@mail.com", role="user"),
            "mentor": User(email="mentor@mail.com", role="mentor"),
            "admin": User(email="admin@mail.com", role="admin"),
        }
        db.session.add_all(users.values())
        db.session.flush()
        apps = {
            "ana_shared": Application(user_id=users["ana"].id, company="Kopi Data", shared_with_mentor_id=users["mentor"].id),
            "ana_private": Application(user_id=users["ana"].id, company="Lintas AI"),
            "budi_private": Application(user_id=users["budi"].id, company="Garuda Pay"),
        }
        db.session.add_all(apps.values())
        db.session.commit()
        app.config["IDS"] = {**{k: v.id for k, v in users.items()}, **{k: v.id for k, v in apps.items()}}
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def ids(app):
    return app.config["IDS"]


def auth(app, who):
    with app.app_context():
        # the token claims "admin" for everyone on purpose: routes must use the DATABASE role
        token = create_access_token(identity=str(app.config["IDS"][who]), additional_claims={"role": "admin"})
    return {"Authorization": f"Bearer {token}"}


def status(response):
    return response.status_code


def test_permissions_module():
    import permissions as p

    assert p.has_permission("admin", "users:list") and not p.has_permission("user", "users:list")
    assert not p.has_permission("hacker", "applications:read_own")

    @p.require_permission("users:list")
    def some_view():
        """doc"""

    assert some_view.__name__ == "some_view"


def test_lists_are_scoped(app, client, ids):
    def listed(who):
        return sorted(a["id"] for a in client.get("/api/v1/applications", headers=auth(app, who)).get_json()["data"])

    assert listed("ana") == sorted([ids["ana_shared"], ids["ana_private"]])
    assert listed("budi") == [ids["budi_private"]]
    assert listed("mentor") == [ids["ana_shared"]]
    assert listed("admin") == sorted([ids["ana_shared"], ids["ana_private"], ids["budi_private"]])


MATRIX = [
    # who, method, application, expected status
    ("ana", "get", "ana_private", 200),
    ("budi", "get", "ana_private", 404),
    ("mentor", "get", "ana_shared", 200),
    ("mentor", "get", "ana_private", 404),
    ("admin", "get", "budi_private", 200),
    ("ana", "patch", "ana_shared", 200),
    ("budi", "patch", "ana_shared", 404),
    ("mentor", "patch", "ana_shared", 403),
    ("mentor", "patch", "budi_private", 404),
    ("admin", "patch", "ana_private", 403),
    ("mentor", "delete", "ana_shared", 403),
    ("budi", "delete", "ana_private", 404),
    ("ana", "delete", "ana_private", 204),
    ("admin", "delete", "budi_private", 204),
]


@pytest.mark.parametrize(("who", "method", "application", "expected"), MATRIX)
def test_permission_matrix(app, client, ids, who, method, application, expected):
    url = f"/api/v1/applications/{ids[application]}"
    response = getattr(client, method)(url, json={"status": "interview"}, headers=auth(app, who))
    assert status(response) == expected, f"{who} {method.upper()} {application}"
    if expected in (403, 404):
        code = response.get_json()["error"]["code"]
        assert code == ("forbidden" if expected == 403 else "application_not_found")


def test_patch_really_updates(app, client, ids):
    response = client.patch(f"/api/v1/applications/{ids['ana_private']}", json={"status": "offer"}, headers=auth(app, "ana"))
    assert response.get_json()["data"]["status"] == "offer"


def test_missing_application_is_404(app, client):
    assert status(client.get("/api/v1/applications/999999", headers=auth(app, "admin"))) == 404


def test_unauthenticated_is_401(client, ids):
    assert status(client.get("/api/v1/applications")) == 401
    assert status(client.get(f"/api/v1/applications/{ids['ana_private']}")) == 401
    assert status(client.get("/api/v1/admin/users")) == 401


def test_admin_users_endpoint(app, client):
    assert status(client.get("/api/v1/admin/users", headers=auth(app, "ana"))) == 403
    body = client.get("/api/v1/admin/users", headers=auth(app, "admin")).get_json()
    assert [u["email"] for u in body["data"]] == ["ana@mail.com", "budi@mail.com", "mentor@mail.com", "admin@mail.com"]
    assert set(body["data"][0]) == {"id", "email", "role"}


def test_demoted_admin_loses_access_immediately(app, client, ids):
    headers = auth(app, "admin")
    assert status(client.get("/api/v1/admin/users", headers=headers)) == 200
    with app.app_context():
        db.session.get(User, ids["admin"]).role = "user"
        db.session.commit()
    assert status(client.get("/api/v1/admin/users", headers=headers)) == 403, "role must come from the database"

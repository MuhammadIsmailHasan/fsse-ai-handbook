"""C4 · Applications, status pipeline and history. Don't edit."""

import re

import pytest
from sqlalchemy import event

STATUSES = ["saved", "applied", "screening", "interview", "offer", "accepted", "rejected", "withdrawn"]
ISO = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d")


def test_create_and_read_application(client, auth, helpers):
    company = helpers.company(client, auth)
    response = client.post(
        "/api/v1/applications",
        json={"company_id": company["id"], "role": " Backend Engineer ", "job_url": "https://jobs.kopidata.id/42", "salary_min": 9_000_000, "salary_max": 14_000_000},
        headers=auth,
    )
    assert response.status_code == 201
    data = response.get_json()["data"]
    assert response.headers["Location"].endswith(f"/api/v1/applications/{data['id']}")
    assert data["company"] == {"id": company["id"], "name": "Kopi Data"}
    assert (data["role"], data["status"], data["applied_on"]) == ("Backend Engineer", "saved", None)
    assert (data["job_url"], data["salary_min"], data["salary_max"]) == ("https://jobs.kopidata.id/42", 9_000_000, 14_000_000)
    assert ISO.match(data["created_at"]) and ISO.match(data["updated_at"])
    assert client.get(f"/api/v1/applications/{data['id']}", headers=auth).get_json()["data"] == data


@pytest.mark.parametrize(
    ("fields", "error_field"),
    [
        ({"role": ""}, "role"),
        ({"salary_min": -1}, "salary_min"),
        ({"salary_min": 15_000_000, "salary_max": 9_000_000}, "salary_max"),
        ({"applied_on": "13/09/2026"}, "applied_on"),
        ({"status": "offer"}, "status"),
    ],
)
def test_application_validation(client, auth, helpers, fields, error_field):
    company = helpers.company(client, auth)
    response = client.post("/api/v1/applications", json={"company_id": company["id"], "role": "Dev", **fields}, headers=auth)
    assert response.status_code == 422 and error_field in response.get_json()["error"]["fields"]


def test_company_must_belong_to_the_user(client, auth, other_auth, helpers):
    foreign = helpers.company(client, other_auth, "Their Company")
    response = client.post("/api/v1/applications", json={"company_id": foreign["id"], "role": "Dev"}, headers=auth)
    assert response.status_code == 422 and "company_id" in response.get_json()["error"]["fields"]
    missing = client.post("/api/v1/applications", json={"company_id": 999_999, "role": "Dev"}, headers=auth)
    assert missing.status_code == 422


def test_patch_updates_fields_and_timestamp(client, auth, helpers):
    company = helpers.company(client, auth)
    created = helpers.application(client, auth, company["id"], salary_min=8_000_000)
    patched = client.patch(f"/api/v1/applications/{created['id']}", json={"role": "Senior Backend Engineer", "applied_on": "2026-09-01"}, headers=auth)
    assert patched.status_code == 200
    data = patched.get_json()["data"]
    assert (data["role"], data["applied_on"], data["salary_min"], data["status"]) == ("Senior Backend Engineer", "2026-09-01", 8_000_000, "saved")
    assert data["updated_at"] >= created["updated_at"]
    assert client.patch(f"/api/v1/applications/{created['id']}", json={"status": "offer"}, headers=auth).status_code == 422, "status only changes via the status endpoint"
    assert client.patch(f"/api/v1/applications/{created['id']}", json={"salary_max": 1}, headers=auth).status_code == 422, "min <= max also on PATCH"


def test_happy_path_pipeline_and_history(client, auth, helpers):
    company = helpers.company(client, auth)
    application = helpers.application(client, auth, company["id"])
    data = helpers.move(client, auth, application["id"], "applied")
    assert re.fullmatch(r"\d{4}-\d\d-\d\d", data["applied_on"]), "moving to applied sets applied_on when empty"
    data = helpers.move(client, auth, application["id"], "screening", "interview", "offer", "accepted")
    assert data["status"] == "accepted"
    history = client.get(f"/api/v1/applications/{application['id']}/history", headers=auth).get_json()["data"]
    assert [(h["from_status"], h["to_status"]) for h in history] == [
        (None, "saved"), ("saved", "applied"), ("applied", "screening"), ("screening", "interview"), ("interview", "offer"), ("offer", "accepted"),
    ]
    assert all(ISO.match(h["changed_at"]) for h in history)


def test_applied_on_is_kept_if_already_set(client, auth, helpers):
    company = helpers.company(client, auth)
    application = helpers.application(client, auth, company["id"], applied_on="2026-08-17")
    assert helpers.move(client, auth, application["id"], "applied")["applied_on"] == "2026-08-17"


ALLOWED = {
    "saved": {"applied", "rejected", "withdrawn"},
    "applied": {"screening", "interview", "rejected", "withdrawn"},
    "screening": {"interview", "rejected", "withdrawn"},
    "interview": {"offer", "rejected", "withdrawn"},
    "offer": {"accepted", "rejected", "withdrawn"},
    "accepted": set(),
    "rejected": set(),
    "withdrawn": set(),
}
PATH_TO = {"saved": [], "applied": ["applied"], "screening": ["applied", "screening"], "interview": ["applied", "interview"], "offer": ["applied", "interview", "offer"], "accepted": ["applied", "interview", "offer", "accepted"], "rejected": ["rejected"], "withdrawn": ["withdrawn"]}


@pytest.mark.parametrize(("current", "target"), [(c, t) for c in STATUSES for t in STATUSES], ids=lambda v: v)
def test_transition_matrix(client, auth, helpers, current, target):
    company = helpers.company(client, auth)
    application = helpers.application(client, auth, company["id"])
    helpers.move(client, auth, application["id"], *PATH_TO[current])
    response = client.post(f"/api/v1/applications/{application['id']}/status", json={"status": target}, headers=auth)
    if target in ALLOWED[current]:
        assert response.status_code == 200 and response.get_json()["data"]["status"] == target
    else:
        assert response.status_code == 409 and response.get_json()["error"]["code"] == "invalid_transition"
        assert client.get(f"/api/v1/applications/{application['id']}", headers=auth).get_json()["data"]["status"] == current


def test_unknown_status_is_422(client, auth, helpers):
    company = helpers.company(client, auth)
    application = helpers.application(client, auth, company["id"])
    response = client.post(f"/api/v1/applications/{application['id']}/status", json={"status": "ghosted"}, headers=auth)
    assert response.status_code == 422


def test_filters_search_and_pagination(client, auth, helpers):
    kopi = helpers.company(client, auth, "Kopi Data")
    awan = helpers.company(client, auth, "Awan Cloud")
    ids = []
    for i in range(25):
        company = kopi if i % 2 == 0 else awan
        role = "Backend Engineer" if i % 3 == 0 else "Data Analyst"
        ids.append(helpers.application(client, auth, company["id"], role=f"{role} {i}")["id"])
    for application_id in ids[:4]:
        helpers.move(client, auth, application_id, "applied")

    first = client.get("/api/v1/applications?per_page=10", headers=auth).get_json()
    assert first["meta"] == {"page": 1, "per_page": 10, "total": 25}
    assert [a["id"] for a in first["data"]] == ids[::-1][:10], "newest first"
    third = client.get("/api/v1/applications?per_page=10&page=3", headers=auth).get_json()
    assert [a["id"] for a in third["data"]] == ids[::-1][20:]
    assert client.get("/api/v1/applications", headers=auth).get_json()["meta"]["per_page"] == 20

    applied = client.get("/api/v1/applications?status=applied", headers=auth).get_json()
    assert sorted(a["id"] for a in applied["data"]) == sorted(ids[:4]) and applied["meta"]["total"] == 4
    by_company = client.get(f"/api/v1/applications?company_id={awan['id']}&q=backend", headers=auth).get_json()
    expected = [ids[i] for i in range(25) if i % 2 == 1 and i % 3 == 0][::-1]
    assert [a["id"] for a in by_company["data"]] == expected

    for bad in ("page=0", "per_page=101", "status=ghosted", "company_id=abc"):
        assert client.get(f"/api/v1/applications?{bad}", headers=auth).status_code == 422, bad


def test_list_does_not_run_n_plus_1_queries(app, client, auth, helpers):
    companies = [helpers.company(client, auth, f"Company {i}") for i in range(10)]
    for company in companies:
        helpers.application(client, auth, company["id"])
    statements = []
    with app.app_context():
        engine = app.extensions["sqlalchemy"].engine
    listener = lambda *args: statements.append(args[2])  # noqa: E731
    event.listen(engine, "before_cursor_execute", listener)
    try:
        response = client.get("/api/v1/applications", headers=auth)
    finally:
        event.remove(engine, "before_cursor_execute", listener)
    assert response.status_code == 200 and len(response.get_json()["data"]) == 10
    assert len(statements) <= 5, f"{len(statements)} queries for one list request — load companies with a join or selectinload"


def test_delete_application_removes_notes_and_history(client, auth, helpers, raw_db):
    company = helpers.company(client, auth)
    application = helpers.application(client, auth, company["id"])
    helpers.move(client, auth, application["id"], "applied")
    client.post(f"/api/v1/applications/{application['id']}/notes", json={"body": "Sent CV"}, headers=auth)
    assert client.delete(f"/api/v1/applications/{application['id']}", headers=auth).status_code == 204
    assert client.get(f"/api/v1/applications/{application['id']}", headers=auth).status_code == 404
    assert client.delete(f"/api/v1/companies/{company['id']}", headers=auth).status_code == 204, "no leftover rows block the company"


def test_users_cannot_access_each_others_applications(client, auth, other_auth, helpers):
    company = helpers.company(client, auth)
    application = helpers.application(client, auth, company["id"])
    base = f"/api/v1/applications/{application['id']}"
    assert client.get("/api/v1/applications", headers=other_auth).get_json()["meta"]["total"] == 0
    assert client.get(base, headers=other_auth).status_code == 404
    assert client.patch(base, json={"role": "x"}, headers=other_auth).status_code == 404
    assert client.post(f"{base}/status", json={"status": "applied"}, headers=other_auth).status_code == 404
    assert client.get(f"{base}/history", headers=other_auth).status_code == 404
    assert client.delete(base, headers=other_auth).status_code == 404

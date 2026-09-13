"""C3 · Companies. Don't edit."""

import pytest


def test_create_list_get_update_delete(client, auth, helpers):
    response = client.post("/api/v1/companies", json={"name": "  Kopi Data ", "website": "https://kopidata.id"}, headers=auth)
    assert response.status_code == 201
    company = response.get_json()["data"]
    assert company == {"id": company["id"], "name": "Kopi Data", "website": "https://kopidata.id"}
    assert response.headers["Location"].endswith(f"/api/v1/companies/{company['id']}")

    helpers.company(client, auth, "awan cloud")
    helpers.company(client, auth, "Batik Soft", website=None)
    names = [c["name"] for c in client.get("/api/v1/companies", headers=auth).get_json()["data"]]
    assert names == ["awan cloud", "Batik Soft", "Kopi Data"], "sorted by name, case-insensitive"

    assert client.get(f"/api/v1/companies/{company['id']}", headers=auth).get_json()["data"] == company
    patched = client.patch(f"/api/v1/companies/{company['id']}", json={"website": "https://new.kopidata.id"}, headers=auth)
    assert patched.status_code == 200 and patched.get_json()["data"]["name"] == "Kopi Data"
    assert patched.get_json()["data"]["website"] == "https://new.kopidata.id"

    assert client.delete(f"/api/v1/companies/{company['id']}", headers=auth).status_code == 204
    assert client.get(f"/api/v1/companies/{company['id']}", headers=auth).status_code == 404


@pytest.mark.parametrize(
    ("body", "field"),
    [({"name": ""}, "name"), ({"name": "x" * 201}, "name"), ({"name": "Ok", "website": "ftp://files.example"}, "website"), ({"name": "Ok", "size": 50}, "size")],
)
def test_company_validation(client, auth, body, field):
    response = client.post("/api/v1/companies", json=body, headers=auth)
    assert response.status_code == 422 and field in response.get_json()["error"]["fields"]


def test_names_are_unique_per_user_case_insensitive(client, auth, other_auth, helpers):
    first = helpers.company(client, auth, "Lintas AI")
    duplicate = client.post("/api/v1/companies", json={"name": "LINTAS ai"}, headers=auth)
    assert duplicate.status_code == 409 and duplicate.get_json()["error"]["code"] == "company_exists"
    assert client.post("/api/v1/companies", json={"name": "Lintas AI"}, headers=other_auth).status_code == 201, "other users may use the same name"
    second = helpers.company(client, auth, "Nusantara Tech")
    rename = client.patch(f"/api/v1/companies/{second['id']}", json={"name": "lintas ai"}, headers=auth)
    assert rename.status_code == 409
    assert helpers.company(client, auth, "After Conflict")["name"] == "After Conflict", "the session must recover after a conflict"
    assert first["id"]


def test_company_in_use_cannot_be_deleted(client, auth, helpers):
    company = helpers.company(client, auth)
    helpers.application(client, auth, company["id"])
    response = client.delete(f"/api/v1/companies/{company['id']}", headers=auth)
    assert response.status_code == 409 and response.get_json()["error"]["code"] == "company_in_use"


def test_users_cannot_see_or_touch_each_others_companies(client, auth, other_auth, helpers):
    company = helpers.company(client, auth)
    assert client.get("/api/v1/companies", headers=other_auth).get_json()["data"] == []
    assert client.get(f"/api/v1/companies/{company['id']}", headers=other_auth).status_code == 404
    assert client.patch(f"/api/v1/companies/{company['id']}", json={"name": "Hacked"}, headers=other_auth).status_code == 404
    assert client.delete(f"/api/v1/companies/{company['id']}", headers=other_auth).status_code == 404
    assert client.get(f"/api/v1/companies/{company['id']}", headers=auth).get_json()["data"]["name"] == "Kopi Data"


def test_companies_require_auth(client):
    assert client.get("/api/v1/companies").status_code == 401

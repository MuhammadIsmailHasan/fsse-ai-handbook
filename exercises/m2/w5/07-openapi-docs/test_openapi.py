"""Checks the generated OpenAPI spec and real behavior. Don't edit this file."""

import pytest

from api import create_app


@pytest.fixture
def client():
    return create_app().test_client()


@pytest.fixture
def spec(client):
    response = client.get("/docs/openapi.json")
    assert response.status_code == 200, "Serve the spec at /docs/openapi.json"
    return response.get_json()


def test_info_and_security_scheme(spec):
    assert spec["info"]["title"] == "CareerPilot API" and spec["info"]["version"] == "v1"
    assert spec["components"]["securitySchemes"]["BearerAuth"] == {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    assert {"name": "companies", "description": "Companies you apply to"} in spec["tags"]


def test_paths_summaries_and_security(spec):
    collection = spec["paths"]["/api/v1/companies"]
    item = spec["paths"]["/api/v1/companies/{company_id}"]
    assert collection["get"]["summary"] == "List companies"
    assert collection["post"]["summary"] == "Create a company"
    assert item["get"]["summary"] == "Get a company"
    assert item["delete"]["summary"] == "Delete a company"
    assert collection["post"]["security"] == [{"BearerAuth": []}]
    assert item["delete"]["security"] == [{"BearerAuth": []}]
    assert "security" not in collection["get"]


def test_documented_responses(spec):
    collection = spec["paths"]["/api/v1/companies"]
    item = spec["paths"]["/api/v1/companies/{company_id}"]
    assert {"200", "422"} <= set(collection["get"]["responses"])
    assert {"201", "409", "422"} <= set(collection["post"]["responses"])
    assert {"200", "404"} <= set(item["get"]["responses"])
    assert {"204", "404"} <= set(item["delete"]["responses"])
    error_ref = collection["post"]["responses"]["409"]["content"]["application/json"]["schema"]["$ref"]
    assert error_ref.endswith("/Error") or error_ref.endswith("/ErrorSchema") or "Error" in error_ref


def test_request_schema_has_description_and_example(spec):
    schemas = spec["components"]["schemas"]
    create = next(schema for name, schema in schemas.items() if name.startswith("CompanyCreate"))
    name = create["properties"]["name"]
    assert name.get("description") and name.get("example") == "Kopi Data"
    assert "name" in create["required"]
    query_params = {p["name"]: p for p in spec["paths"]["/api/v1/companies"]["get"]["parameters"]}
    assert {"q", "page"} <= set(query_params)


def test_behavior_matches_docs(client):
    created = client.post("/api/v1/companies", json={"name": "Kopi Data", "website": "https://kopidata.id"})
    assert created.status_code == 201
    company = created.get_json()
    assert company == {"id": 1, "name": "Kopi Data", "website": "https://kopidata.id"}
    assert client.post("/api/v1/companies", json={"name": "kopi data"}).get_json()["error"]["code"] == "company_exists"
    assert client.get("/api/v1/companies?q=KOPI").get_json()[0]["id"] == 1
    assert client.get("/api/v1/companies/1").status_code == 200
    missing = client.get("/api/v1/companies/99")
    assert missing.status_code == 404 and missing.get_json()["error"]["code"] == "company_not_found"
    assert client.delete("/api/v1/companies/1").status_code == 204
    assert client.delete("/api/v1/companies/1").status_code == 404


def test_validation_uses_handbook_envelope(client):
    body = client.post("/api/v1/companies", json={"website": "not a url", "extra": 1}).get_json()
    assert body["error"]["code"] == "validation_failed"
    assert {"json.name", "json.website", "json.extra"} <= set(body["error"]["fields"])
    query = client.get("/api/v1/companies?page=0")
    assert query.status_code == 422 and "query.page" in query.get_json()["error"]["fields"]

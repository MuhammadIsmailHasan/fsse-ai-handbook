"""Tests for schemas.py and api.py. Don't edit this file."""

from datetime import date, timedelta

import pytest
from marshmallow import ValidationError

from api import create_app
from schemas import ApplicationCreateSchema, ApplicationResponseSchema, SalarySchema, flatten_errors

VALID = {"company": "Kopi Data", "role_title": "Data Analyst"}


def errors_for(data, **schema_kwargs):
    with pytest.raises(ValidationError) as info:
        ApplicationCreateSchema(**schema_kwargs).load(data)
    return info.value.messages


def test_defaults_and_cleaning():
    data = ApplicationCreateSchema().load(
        {"company": "  Kopi Data ", "role_title": " Analyst", "contact_email": " HR@KopiData.ID ", "tags": [" SQL", "Python "]}
    )
    assert data == {
        "company": "Kopi Data",
        "role_title": "Analyst",
        "status": "applied",
        "applied_on": None,
        "contact_email": "hr@kopidata.id",
        "salary": None,
        "tags": ["sql", "python"],
    }


def test_default_tags_are_not_shared():
    first = ApplicationCreateSchema().load(VALID)
    first["tags"].append("mutated")
    assert ApplicationCreateSchema().load(VALID)["tags"] == []


def test_required_and_blank():
    messages = errors_for({"company": "   "})
    assert set(messages) == {"company", "role_title"}


def test_unknown_and_invalid_values():
    messages = errors_for({**VALID, "user_id": 3, "status": "hired", "contact_email": "nope", "applied_on": "13/09/2026"})
    assert {"user_id", "status", "contact_email", "applied_on"} <= set(messages)


def test_future_date_rejected_today_allowed():
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    assert errors_for({**VALID, "applied_on": tomorrow})["applied_on"] == ["can't be in the future"]
    assert ApplicationCreateSchema().load({**VALID, "applied_on": date.today().isoformat()})["applied_on"] == date.today()


def test_salary_nested_rules():
    assert SalarySchema().load({"min": 1, "max": 2}) == {"min": 1, "max": 2, "currency": "IDR"}
    messages = errors_for({**VALID, "salary": {"min": 10_000_000, "max": 9_000_000, "currency": "EUR"}})
    assert messages["salary"]["max"] == ["must be greater than or equal to min"]
    assert "currency" in messages["salary"]
    assert ApplicationCreateSchema().load({**VALID, "salary": None})["salary"] is None


def test_tag_rules():
    assert errors_for({**VALID, "tags": ["sql", "SQL"]})["tags"] == ["tags must be unique"]
    assert "tags" in errors_for({**VALID, "tags": [f"t{i}" for i in range(11)]})
    assert "1" in {str(k) for k in errors_for({**VALID, "tags": ["ok", "x" * 31]})["tags"]}


def test_partial_update():
    assert ApplicationCreateSchema(partial=True).load({"status": "interview"}) == {"status": "interview"}


def test_response_schema_hides_internal_fields():
    dumped = ApplicationResponseSchema().dump(
        {"id": 1, "user_id": 7, "private_notes": "x", "company": "A", "role_title": "B", "status": "applied",
         "applied_on": date(2026, 9, 1), "salary": {"min": 1, "max": 2, "currency": "IDR"}, "tags": ["sql"]}
    )
    assert dumped == {"id": 1, "company": "A", "role_title": "B", "status": "applied", "applied_on": "2026-09-01",
                      "salary": {"min": 1, "max": 2, "currency": "IDR"}, "tags": ["sql"]}


def test_flatten_errors():
    assert flatten_errors(
        {"company": ["Missing."], "salary": {"max": ["too small", "second"]}, "tags": {1: ["too long"]}, "_schema": ["Invalid input type."]}
    ) == {"company": "Missing.", "salary.max": "too small", "tags.1": "too long", "body": "Invalid input type."}


@pytest.fixture
def client():
    return create_app().test_client()


def test_api_created(client):
    response = client.post("/applications", json={**VALID, "tags": ["SQL"]})
    assert response.status_code == 201
    data = response.get_json()["data"]
    assert data["id"] == 1 and "user_id" not in data and "private_notes" not in data and data["tags"] == ["sql"]


def test_api_400_for_non_object(client):
    assert client.post("/applications", data="{bad", content_type="application/json").status_code == 400
    assert client.post("/applications", json=[1, 2]).get_json()["error"]["code"] == "invalid_json"


def test_api_422_with_flat_fields(client):
    response = client.post("/applications", json={"company": "", "salary": {"min": 5, "max": 1}})
    assert response.status_code == 422
    error = response.get_json()["error"]
    assert error["code"] == "validation_failed" and error["message"] == "Some fields are invalid"
    assert {"company", "role_title", "salary.max"} <= set(error["fields"])

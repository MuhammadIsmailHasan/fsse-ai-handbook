"""Tests for errors.py. Don't edit this file."""

import pytest

import errors as e


def test_hierarchy_and_codes():
    assert issubclass(e.ApplicationNotFound, e.NotFound) and issubclass(e.NotFound, e.AppError)
    for cls, status, code in [
        (e.AppError, 500, "internal_error"),
        (e.NotFound, 404, "not_found"),
        (e.Conflict, 409, "conflict"),
        (e.ValidationFailed, 422, "validation_failed"),
        (e.ApplicationNotFound, 404, "application_not_found"),
        (e.ServiceUnavailable, 503, "service_unavailable"),
    ]:
        assert (cls.status_code, cls.code) == (status, code)
    error = e.ApplicationNotFound(7)
    assert str(error) == "application 7 not found" and error.application_id == 7


def test_parse_application_valid():
    assert e.parse_application({"company": " Kopi Data ", "role_title": "Analyst", "salary_expectation": "12000000"}) == {
        "company": "Kopi Data",
        "role_title": "Analyst",
        "salary_expectation": 12_000_000,
    }
    assert e.parse_application({"company": "X", "role_title": "Y"})["salary_expectation"] is None


def test_parse_application_collects_all_errors():
    with pytest.raises(e.ValidationFailed) as info:
        e.parse_application({"company": "   ", "salary_expectation": -5})
    assert info.value.errors == {
        "company": "required",
        "role_title": "required",
        "salary_expectation": "must be a non-negative integer",
    }


@pytest.mark.parametrize("salary", ["abc", 3.5, "-1", True])
def test_parse_application_bad_salary(salary):
    with pytest.raises(e.ValidationFailed) as info:
        e.parse_application({"company": "X", "role_title": "Y", "salary_expectation": salary})
    assert info.value.errors == {"salary_expectation": "must be a non-negative integer"}


def test_load_application_translates_and_chains():
    def down(_id):
        raise ConnectionError("socket closed")

    with pytest.raises(e.ServiceUnavailable) as info:
        e.load_application(down, 1)
    assert isinstance(info.value.__cause__, ConnectionError)

    with pytest.raises(e.ApplicationNotFound):
        e.load_application(lambda _id: None, 3)

    assert e.load_application(lambda _id: {"id": _id}, 5) == {"id": 5}


def test_to_response_known_errors():
    assert e.to_response(e.ApplicationNotFound(9)) == (
        {"error": {"code": "application_not_found", "message": "application 9 not found"}},
        404,
    )
    body, status = e.to_response(e.ValidationFailed({"company": "required"}))
    assert status == 422
    assert body["error"]["fields"] == {"company": "required"}


def test_to_response_hides_unexpected_details():
    body, status = e.to_response(KeyError("password_hash column missing"))
    assert status == 500
    assert body == {"error": {"code": "internal_error", "message": "Something went wrong"}}


def test_timer_records_even_on_error():
    records = []
    with e.timer("ok", records):
        pass
    with pytest.raises(RuntimeError):
        with e.timer("boom", records):
            raise RuntimeError("fail")
    assert [name for name, _ in records] == ["ok", "boom"]
    assert all(seconds >= 0 for _, seconds in records)

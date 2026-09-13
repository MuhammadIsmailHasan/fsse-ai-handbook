"""Reference solution."""

import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager


class AppError(Exception):
    status_code = 500
    code = "internal_error"


class NotFound(AppError):
    status_code = 404
    code = "not_found"


class Conflict(AppError):
    status_code = 409
    code = "conflict"


class ValidationFailed(AppError):
    status_code = 422
    code = "validation_failed"

    def __init__(self, errors: dict[str, str]):
        super().__init__("validation failed")
        self.errors = errors


class ApplicationNotFound(NotFound):
    code = "application_not_found"

    def __init__(self, application_id: int):
        super().__init__(f"application {application_id} not found")
        self.application_id = application_id


class ServiceUnavailable(AppError):
    status_code = 503
    code = "service_unavailable"


def _required_text(data: dict, field: str, errors: dict[str, str]) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        errors[field] = "required"
        return ""
    return value.strip()


def _optional_non_negative_int(value: object) -> int | None:
    """Return the parsed int, or raise ValueError."""
    if value is None:
        return None
    if isinstance(value, bool):  # bool is a subclass of int — reject it explicitly
        raise ValueError
    if isinstance(value, int):
        number = value
    elif isinstance(value, str) and value.strip().isdigit():
        number = int(value.strip())
    else:
        raise ValueError
    if number < 0:
        raise ValueError
    return number


def parse_application(data: dict) -> dict:
    errors: dict[str, str] = {}
    company = _required_text(data, "company", errors)
    role_title = _required_text(data, "role_title", errors)
    try:
        salary = _optional_non_negative_int(data.get("salary_expectation"))
    except ValueError:
        errors["salary_expectation"] = "must be a non-negative integer"
        salary = None
    if errors:
        raise ValidationFailed(errors)
    return {"company": company, "role_title": role_title, "salary_expectation": salary}


def load_application(fetch: Callable[[int], dict | None], application_id: int) -> dict:
    try:
        application = fetch(application_id)
    except ConnectionError as error:
        raise ServiceUnavailable("database unavailable") from error
    if application is None:
        raise ApplicationNotFound(application_id)
    return application


def to_response(error: Exception) -> tuple[dict, int]:
    if isinstance(error, AppError):
        body: dict = {"code": error.code, "message": str(error)}
        if isinstance(error, ValidationFailed):
            body["fields"] = error.errors
        return {"error": body}, error.status_code
    # Unknown errors: log the details server-side (not shown here), return nothing internal.
    return {"error": {"code": "internal_error", "message": "Something went wrong"}}, 500


@contextmanager
def timer(name: str, records: list) -> Iterator[None]:
    start = time.perf_counter()
    try:
        yield
    finally:
        records.append((name, time.perf_counter() - start))

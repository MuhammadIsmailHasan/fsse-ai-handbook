"""M2 · W3 · 08 — Error hierarchy and a safe boundary."""

from contextlib import contextmanager  # noqa: F401


class AppError(Exception):
    pass


# YOUR CODE HERE: NotFound, Conflict, ValidationFailed, ApplicationNotFound, ServiceUnavailable


def parse_application(data: dict) -> dict:
    # YOUR CODE HERE
    return {}


def load_application(fetch, application_id: int) -> dict:
    # YOUR CODE HERE
    return fetch(application_id)


def to_response(error: Exception) -> tuple[dict, int]:
    # YOUR CODE HERE
    return {}, 200


def timer(name: str, records: list):
    # YOUR CODE HERE (make this a context manager)
    raise NotImplementedError

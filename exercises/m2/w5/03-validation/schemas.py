"""M2 · W5 · 03 — marshmallow 4 schemas."""

from marshmallow import Schema, ValidationError, fields, pre_load, validate, validates, validates_schema  # noqa: F401


class SalarySchema(Schema):
    pass  # YOUR CODE HERE


class ApplicationCreateSchema(Schema):
    pass  # YOUR CODE HERE


class ApplicationResponseSchema(Schema):
    pass  # YOUR CODE HERE


def flatten_errors(messages: dict, prefix: str = "") -> dict[str, str]:
    # YOUR CODE HERE
    return {}

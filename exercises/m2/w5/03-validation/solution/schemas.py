"""Reference solution."""

from datetime import date

from marshmallow import Schema, ValidationError, fields, pre_load, validate, validates, validates_schema


class SalarySchema(Schema):
    min = fields.Integer(required=True, validate=validate.Range(min=0))
    max = fields.Integer(required=True, validate=validate.Range(min=0))
    currency = fields.String(load_default="IDR", validate=validate.OneOf(["IDR", "USD", "SGD"]))

    # By default marshmallow SKIPS schema validators when any field already has an error.
    # skip_on_field_errors=False reports this rule too, so the client sees all problems at once.
    @validates_schema(skip_on_field_errors=False)
    def max_not_below_min(self, data, **kwargs):
        low, high = data.get("min"), data.get("max")  # a field may be missing if it failed validation
        if isinstance(low, int) and isinstance(high, int) and high < low:
            raise ValidationError("must be greater than or equal to min", field_name="max")


class ApplicationCreateSchema(Schema):
    company = fields.String(required=True, validate=validate.Length(min=1, max=200))
    role_title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    status = fields.String(load_default="applied", validate=validate.OneOf(["wishlist", "applied", "interview"]))
    applied_on = fields.Date(load_default=None, allow_none=True)
    contact_email = fields.Email(load_default=None, allow_none=True)
    salary = fields.Nested(SalarySchema, load_default=None, allow_none=True)
    tags = fields.List(
        fields.String(validate=validate.Length(min=1, max=30)),
        load_default=list,  # a callable: each load gets its own new list
        validate=validate.Length(max=10),
    )

    @pre_load
    def clean_strings(self, data, **kwargs):
        if not isinstance(data, dict):
            return data  # let marshmallow report "Invalid input type."
        cleaned = {key: value.strip() if isinstance(value, str) else value for key, value in data.items()}
        if isinstance(cleaned.get("contact_email"), str):
            cleaned["contact_email"] = cleaned["contact_email"].lower()
        if isinstance(cleaned.get("tags"), list):
            cleaned["tags"] = [tag.strip().lower() if isinstance(tag, str) else tag for tag in cleaned["tags"]]
        return cleaned

    @validates("applied_on")
    def not_in_future(self, value, **kwargs):
        if value is not None and value > date.today():
            raise ValidationError("can't be in the future")

    @validates("tags")
    def unique_tags(self, value, **kwargs):
        if len(value) != len(set(value)):
            raise ValidationError("tags must be unique")


class ApplicationResponseSchema(Schema):
    id = fields.Integer()
    company = fields.String()
    role_title = fields.String()
    status = fields.String()
    applied_on = fields.Date(allow_none=True)
    salary = fields.Nested(SalarySchema, allow_none=True)
    tags = fields.List(fields.String())


def flatten_errors(messages: dict, prefix: str = "") -> dict[str, str]:
    flat: dict[str, str] = {}
    for key, value in messages.items():
        name = "body" if key == "_schema" and not prefix else str(key)
        path = f"{prefix}.{name}" if prefix else name
        if isinstance(value, dict):
            flat.update(flatten_errors(value, path))
        elif isinstance(value, list):
            flat[path] = str(value[0])
        else:
            flat[path] = str(value)
    return flat

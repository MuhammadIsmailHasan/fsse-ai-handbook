"""Reference solution."""

from flask import Flask, current_app
from flask.views import MethodView
from flask_smorest import Api, Blueprint, abort
from marshmallow import Schema, fields, validate

blp = Blueprint("companies", __name__, url_prefix="/api/v1/companies", description="Companies you apply to")


class CompanyQuerySchema(Schema):
    q = fields.String(metadata={"description": "Case-insensitive search on the company name", "example": "kopi"})
    page = fields.Integer(load_default=1, validate=validate.Range(min=1), metadata={"description": "Page number"})


class CompanyCreateSchema(Schema):
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200),
        metadata={"description": "Company name, unique (case-insensitive)", "example": "Kopi Data"},
    )
    website = fields.Url(metadata={"description": "Public website", "example": "https://kopidata.id"})


class CompanySchema(Schema):
    id = fields.Integer(dump_only=True, metadata={"example": 1})
    name = fields.String(metadata={"example": "Kopi Data"})
    website = fields.String(allow_none=True, metadata={"example": "https://kopidata.id"})


class ErrorBodySchema(Schema):
    code = fields.String(metadata={"example": "company_not_found"})
    message = fields.String(metadata={"example": "Company 42 not found"})


class ErrorSchema(Schema):
    error = fields.Nested(ErrorBodySchema)


def store() -> list[dict]:
    return current_app.extensions["companies"]


def error(status: int, code: str, message: str):
    abort(status, message=message, code=code)


def find(company_id: int) -> dict:
    company = next((c for c in store() if c["id"] == company_id), None)
    if company is None:
        error(404, "company_not_found", f"Company {company_id} not found")
    return company


@blp.route("")
class Companies(MethodView):
    @blp.arguments(CompanyQuerySchema, location="query")
    @blp.response(200, CompanySchema(many=True))
    def get(self, query):
        """List companies

        Sorted by insertion order. Use `q` to search by name (case-insensitive).
        """
        q = (query.get("q") or "").lower()
        return [c for c in store() if q in c["name"].lower()]

    @blp.arguments(CompanyCreateSchema)
    @blp.response(201, CompanySchema)
    @blp.alt_response(409, schema=ErrorSchema, description="A company with this name already exists")
    @blp.doc(security=[{"BearerAuth": []}])
    def post(self, data):
        """Create a company"""
        if any(c["name"].lower() == data["name"].lower() for c in store()):
            error(409, "company_exists", f"A company named {data['name']!r} already exists")
        company = {"id": max((c["id"] for c in store()), default=0) + 1, "website": None, **data}
        store().append(company)
        return company


@blp.route("/<int:company_id>")
class CompanyItem(MethodView):
    @blp.response(200, CompanySchema)
    @blp.alt_response(404, schema=ErrorSchema, description="Company not found")
    def get(self, company_id):
        """Get a company"""
        return find(company_id)

    @blp.response(204)
    @blp.alt_response(404, schema=ErrorSchema, description="Company not found")
    @blp.doc(security=[{"BearerAuth": []}])
    def delete(self, company_id):
        """Delete a company"""
        store().remove(find(company_id))


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        API_TITLE="CareerPilot API",
        API_VERSION="v1",
        OPENAPI_VERSION="3.0.3",
        OPENAPI_URL_PREFIX="/docs",
        OPENAPI_JSON_PATH="openapi.json",
        OPENAPI_SWAGGER_UI_PATH="/swagger-ui",
        OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
    )
    app.extensions["companies"] = []
    api = Api(app)
    api.spec.components.security_scheme("BearerAuth", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"})
    api.register_blueprint(blp)

    @app.errorhandler(422)
    def validation_error(err):
        messages = getattr(err, "data", {}).get("messages", {})
        flat = {
            f"{location}.{field}": (errors[0] if isinstance(errors, list) else str(errors))
            for location, by_field in messages.items()
            for field, errors in by_field.items()
        }
        return {"error": {"code": "validation_failed", "message": "Some fields are invalid", "fields": flat}}, 422

    for status in (404, 409):
        def handler(err, status=status):
            data = getattr(err, "data", {}) or {}
            code = data.get("code") or ("not_found" if status == 404 else "conflict")
            message = data.get("message") or getattr(err, "description", "")
            return {"error": {"code": code, "message": message}}, status

        app.register_error_handler(status, handler)

    return app

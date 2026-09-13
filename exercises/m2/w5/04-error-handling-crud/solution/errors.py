"""Reference solution."""

import re
import uuid

from flask import Flask, g, request
from werkzeug.exceptions import HTTPException

REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9-]{1,64}$")


class AppError(Exception):
    status_code = 500
    code = "internal_error"

    def __init__(self, message: str = "", code: str | None = None):
        super().__init__(message)
        if code is not None:
            self.code = code


class NotFound(AppError):
    status_code = 404
    code = "not_found"


class Conflict(AppError):
    status_code = 409
    code = "conflict"


class ValidationFailed(AppError):
    status_code = 422
    code = "validation_failed"

    def __init__(self, fields: dict[str, str], message: str = "Some fields are invalid"):
        super().__init__(message)
        self.fields = fields


def error_body(code: str, message: str, fields: dict | None = None) -> dict:
    body = {"code": code, "message": message, "request_id": getattr(g, "request_id", None)}
    if fields:
        body["fields"] = fields
    return {"error": body}


def register_error_handlers(app: Flask) -> None:
    @app.before_request
    def assign_request_id():
        incoming = request.headers.get("X-Request-ID", "")
        g.request_id = incoming if REQUEST_ID_PATTERN.fullmatch(incoming) else uuid.uuid4().hex

    @app.after_request
    def return_request_id(response):
        response.headers["X-Request-ID"] = getattr(g, "request_id", "")
        return response

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return error_body(error.code, str(error), getattr(error, "fields", None)), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        code = (error.name or "error").lower().replace(" ", "_")
        return error_body(code, error.description or ""), error.code

    @app.errorhandler(Exception)
    def handle_unexpected(error: Exception):
        app.logger.exception("Unhandled error [request_id=%s]", getattr(g, "request_id", "-"))
        return error_body("internal_error", "Something went wrong"), 500

"""JSON error handlers for the whole app."""

from flask import Flask
from werkzeug.exceptions import HTTPException


def error_body(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message}}


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        code = (error.name or "error").lower().replace(" ", "_")
        return error_body(code, error.description or ""), error.code

    @app.errorhandler(Exception)
    def handle_unexpected(error: Exception):
        app.logger.exception("Unhandled error")
        return error_body("internal_error", "Something went wrong"), 500

"""Provided: app factory and a JSON error type."""

from flask import Flask

from models import db


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str, fields: dict | None = None):
        super().__init__(message)
        self.status, self.code, self.message, self.fields = status, code, message, fields


def create_app(database_url: str) -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    db.init_app(app)

    from jobs import jobs_bp

    app.register_blueprint(jobs_bp)

    @app.errorhandler(ApiError)
    def handle(error: ApiError):
        body = {"code": error.code, "message": error.message}
        if error.fields:
            body["fields"] = error.fields
        return {"error": body}, error.status

    return app

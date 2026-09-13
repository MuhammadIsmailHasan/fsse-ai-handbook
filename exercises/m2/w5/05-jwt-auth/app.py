"""Provided: application factory."""

from datetime import timedelta

from flask import Flask

from models import db


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str, fields: dict | None = None):
        super().__init__(message)
        self.status, self.code, self.message, self.fields = status, code, message, fields


def create_app(database_url: str) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=database_url,
        JWT_SECRET_KEY="test-only-secret-key-with-at-least-32-bytes!!",  # real apps: from the environment
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=15),
        JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=30),
    )
    db.init_app(app)

    from auth import auth_bp, init_auth

    init_auth(app)
    app.register_blueprint(auth_bp)

    @app.errorhandler(ApiError)
    def handle(error: ApiError):
        body = {"code": error.code, "message": error.message}
        if error.fields:
            body["fields"] = error.fields
        return {"error": body}, error.status

    return app

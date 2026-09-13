"""Provided: factory with JWT authentication (current_user loaded from the database)."""

from flask import Flask
from flask_jwt_extended import JWTManager

from models import User, db


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status, self.code, self.message = status, code, message


def create_app(database_url: str) -> Flask:
    app = Flask(__name__)
    app.config.update(SQLALCHEMY_DATABASE_URI=database_url, JWT_SECRET_KEY="test-only-secret-key-with-at-least-32-bytes!!")
    db.init_app(app)
    jwt = JWTManager(app)

    def unauthorized(code, message):
        return {"error": {"code": code, "message": message}}, 401

    jwt.unauthorized_loader(lambda reason: unauthorized("token_missing", reason))
    jwt.invalid_token_loader(lambda reason: unauthorized("token_invalid", reason))
    jwt.expired_token_loader(lambda header, payload: unauthorized("token_expired", "Token has expired"))
    jwt.user_lookup_error_loader(lambda header, payload: unauthorized("user_not_found", "User no longer exists"))

    @jwt.user_lookup_loader
    def load_user(jwt_header, jwt_payload):
        return db.session.get(User, int(jwt_payload["sub"]))

    @app.errorhandler(ApiError)
    def handle(error: ApiError):
        return {"error": {"code": error.code, "message": error.message}}, error.status

    from applications import admin_bp, applications_bp

    app.register_blueprint(applications_bp)
    app.register_blueprint(admin_bp)
    return app

"""Provided: application factory wiring the layers together."""

from flask import Flask

from .errors import AppError
from .models import db


def create_app(database_url: str) -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    db.init_app(app)

    from .routes import applications_bp

    app.register_blueprint(applications_bp)

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        body = {"code": error.code, "message": str(error)}
        if getattr(error, "fields", None):
            body["fields"] = error.fields
        return {"error": body}, error.status_code

    return app

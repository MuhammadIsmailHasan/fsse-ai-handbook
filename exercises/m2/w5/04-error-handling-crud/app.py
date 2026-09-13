"""Provided: application factory."""

from flask import Flask

from models import db


def create_app(database_url: str) -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    db.init_app(app)

    from companies import companies_bp
    from errors import register_error_handlers

    app.register_blueprint(companies_bp)
    register_error_handlers(app)
    return app

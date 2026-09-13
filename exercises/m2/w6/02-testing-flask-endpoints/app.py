"""Provided: application factory."""

from flask import Flask

from models import db


def create_app(database_url: str, api_key: str = "dev-key") -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["API_KEY"] = api_key
    db.init_app(app)

    from api import bp

    app.register_blueprint(bp)
    return app

"""Provided: a minimal app factory for the exercise."""

from flask import Flask

from models import db


def create_app(database_url: str) -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
    db.init_app(app)
    return app

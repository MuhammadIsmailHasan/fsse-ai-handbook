"""Provided: app factory wiring Flask-SQLAlchemy and Flask-Migrate."""

from pathlib import Path

from flask import Flask
from flask_migrate import Migrate

from models import db

MIGRATIONS_DIR = str(Path(__file__).parent / "migrations")


def create_app(database_url: str) -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    db.init_app(app)
    Migrate(app, db, directory=MIGRATIONS_DIR)
    return app

"""CareerPilot API — Phase 2.

The acceptance tests call:

    create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "...", "JWT_SECRET_KEY": "..."})

and then run your Alembic migrations from ./migrations with Flask-Migrate.
Values passed in `config` must override anything loaded from the environment.
"""

from flask import Flask


def create_app(config: dict | None = None) -> Flask:
    raise NotImplementedError("Build the app factory — start with checkpoint C1 in README.md")

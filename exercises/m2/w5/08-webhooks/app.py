"""Provided: application factory."""

import time

from flask import Flask

from models import db


def create_app(database_url: str, clock=time.time) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=database_url,
        WEBHOOK_SECRET="whsec_test_only_1234567890",  # real apps: from the environment
        CLOCK=clock,
    )
    db.init_app(app)

    from webhooks import webhooks_bp

    app.register_blueprint(webhooks_bp)
    return app

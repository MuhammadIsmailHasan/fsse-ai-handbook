"""Provided: application factory configured from the environment."""

import os

from flask import Flask, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix

from extensions import db


def create_app(database_url: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or os.environ["DATABASE_URL"]
    # Fail fast on a dead database instead of hanging a worker.
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True, "connect_args": {"connect_timeout": 3}}
    db.init_app(app)

    if os.environ.get("TRUST_PROXY") == "1":
        # Behind ONE reverse proxy / load balancer: trust its X-Forwarded-For / -Proto / -Host headers.
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    from health import health_bp

    app.register_blueprint(health_bp)

    @app.get("/api/v1/whoami")
    def whoami():
        return jsonify({"scheme": request.scheme, "remote_addr": request.remote_addr, "pid": os.getpid()})

    return app

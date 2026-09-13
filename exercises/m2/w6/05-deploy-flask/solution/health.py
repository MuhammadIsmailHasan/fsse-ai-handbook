"""Liveness and readiness endpoints for load balancers and orchestrators."""

import logging

from flask import Blueprint, jsonify
from sqlalchemy import text

from extensions import db

health_bp = Blueprint("health", __name__, url_prefix="/health")
logger = logging.getLogger(__name__)


@health_bp.get("/live")
def live():
    # "Is the process alive?" — never touches dependencies, so a DB outage doesn't restart every container.
    return jsonify({"status": "ok"}), 200, {"Cache-Control": "no-store"}


@health_bp.get("/ready")
def ready():
    # "Can this instance serve traffic right now?"
    try:
        db.session.execute(text("SELECT 1"))
        database = "ok"
    except Exception:
        logger.exception("readiness check: database unavailable")
        db.session.rollback()
        database = "fail"
    healthy = database == "ok"
    body = {"status": "ok" if healthy else "unavailable", "checks": {"database": database}}
    return jsonify(body), 200 if healthy else 503, {"Cache-Control": "no-store"}

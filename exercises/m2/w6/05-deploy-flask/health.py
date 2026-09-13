"""Liveness and readiness endpoints. See README.md."""

from flask import Blueprint

health_bp = Blueprint("health", __name__, url_prefix="/health")

# TODO GET /health/live
# TODO GET /health/ready

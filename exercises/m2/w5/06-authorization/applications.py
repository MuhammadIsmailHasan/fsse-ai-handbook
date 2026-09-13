"""M2 · W5 · 06 — Routes using the permission rules."""

from flask import Blueprint

applications_bp = Blueprint("applications", __name__, url_prefix="/api/v1/applications")
admin_bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")

# YOUR CODE HERE

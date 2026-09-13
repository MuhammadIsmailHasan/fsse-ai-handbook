"""M2 · W4 · 06 — YOUR HTTP layer: parse the request, call the service, format the response."""

from flask import Blueprint

applications_bp = Blueprint("applications", __name__, url_prefix="/api/v1/applications")

# YOUR CODE HERE

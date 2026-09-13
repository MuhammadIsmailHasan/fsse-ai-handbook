"""Reference solution: thin HTTP layer."""

from datetime import datetime, timezone

from flask import Blueprint, request

from .errors import AppError
from .models import Application
from .repositories import SqlApplicationRepository
from .services import ApplicationService

applications_bp = Blueprint("applications", __name__, url_prefix="/api/v1/applications")


class Unauthorized(AppError):
    status_code = 401
    code = "unauthorized"


def current_user_id() -> int:
    raw = request.headers.get("X-User-Id", "")
    if not raw.isdigit():
        raise Unauthorized("missing or invalid X-User-Id header")
    return int(raw)


def service() -> ApplicationService:
    return ApplicationService(SqlApplicationRepository(), clock=lambda: datetime.now(timezone.utc))


def serialize(application: Application) -> dict:
    return {
        "id": application.id,
        "company": application.company,
        "role_title": application.role_title,
        "status": application.status,
    }


@applications_bp.post("")
def create_application():
    application = service().create(current_user_id(), request.get_json(silent=True) or {})
    return {"data": serialize(application)}, 201


@applications_bp.get("")
def list_applications():
    return {"data": [serialize(a) for a in service().list(current_user_id())]}


@applications_bp.post("/<int:application_id>/status")
def change_status(application_id: int):
    body = request.get_json(silent=True) or {}
    application = service().change_status(current_user_id(), application_id, str(body.get("status", "")))
    return {"data": serialize(application)}

"""Reference solution."""

from flask import Blueprint, request
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy import select

from app import ApiError
from models import Application, User, db
from permissions import can_delete, can_edit, can_view, require_permission, visible_applications_query

applications_bp = Blueprint("applications", __name__, url_prefix="/api/v1/applications")
admin_bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")


def serialize(application: Application) -> dict:
    return {"id": application.id, "user_id": application.user_id, "company": application.company, "status": application.status}


def visible_or_404(application_id: int) -> Application:
    application = db.session.get(Application, application_id)
    if application is None or not can_view(current_user, application):
        raise ApiError(404, "application_not_found", f"Application {application_id} not found")
    return application


@applications_bp.get("")
@jwt_required()
def list_applications():
    stmt = visible_applications_query(current_user).order_by(Application.id)  # scoped in SQL, not in Python
    return {"data": [serialize(a) for a in db.session.scalars(stmt)]}


@applications_bp.get("/<int:application_id>")
@jwt_required()
def get_application(application_id: int):
    return {"data": serialize(visible_or_404(application_id))}


@applications_bp.patch("/<int:application_id>")
@jwt_required()
def update_application(application_id: int):
    application = visible_or_404(application_id)
    if not can_edit(current_user, application):
        raise ApiError(403, "forbidden", "You can view but not edit this application")
    application.status = str((request.get_json(silent=True) or {}).get("status", application.status))
    db.session.commit()
    return {"data": serialize(application)}


@applications_bp.delete("/<int:application_id>")
@jwt_required()
def delete_application(application_id: int):
    application = visible_or_404(application_id)
    if not can_delete(current_user, application):
        raise ApiError(403, "forbidden", "You can't delete this application")
    db.session.delete(application)
    db.session.commit()
    return "", 204


@admin_bp.get("/users")
@require_permission("users:list")
def list_users():
    users = db.session.scalars(select(User).order_by(User.id))
    return {"data": [{"id": u.id, "email": u.email, "role": u.role} for u in users]}

"""Applications API. This implementation is CORRECT — write integration tests for it.

All errors look like: {"error": {"code": "<code>"}}

POST   /api/v1/applications               body {"company", "role"} (non-blank strings)
       → 201 {"data": {...status "saved"}} + Location header
       → 401 unauthorized  (header X-API-Key missing or != app.config["API_KEY"])
       → 422 validation_failed
GET    /api/v1/applications[?status=...]  → 200 {"data": [...]} ordered by id; unknown status → 422 validation_failed
GET    /api/v1/applications/<id>          → 200 {"data": {...}} | 404 not_found
PATCH  /api/v1/applications/<id>/status   body {"status"}  (requires X-API-Key)
       allowed: saved→applied, applied→interview, interview→offer, and ANY non-final status → rejected
       ("offer" and "rejected" are final)
       → 200 {"data": {...}} | 401 | 404 not_found | 409 invalid_transition | 422 validation_failed
DELETE /api/v1/applications/<id>          (requires X-API-Key) → 204 | 401 | 404 not_found
"""

import hmac

from flask import Blueprint, current_app, jsonify, request, url_for

from models import Application, db

bp = Blueprint("applications", __name__, url_prefix="/api/v1/applications")

STATUSES = ("saved", "applied", "interview", "offer", "rejected")
NEXT = {"saved": {"applied", "rejected"}, "applied": {"interview", "rejected"}, "interview": {"offer"}}


def error(code: str, status: int):
    return jsonify({"error": {"code": code}}), status


def authorized() -> bool:
    given = request.headers.get("X-API-Key", "")
    return hmac.compare_digest(given.encode(), current_app.config["API_KEY"].encode())


def non_blank(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


@bp.post("")
def create_application():
    if not authorized():
        return error("unauthorized", 401)
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or not non_blank(body.get("company")) or not non_blank(body.get("role")):
        return error("validation_failed", 422)
    application = Application(company=body["company"].strip(), role=body["role"].strip(), status="saved")
    db.session.add(application)
    db.session.commit()
    location = url_for("applications.get_application", application_id=application.id)
    return jsonify({"data": application.to_dict()}), 201, {"Location": location}


@bp.get("")
def list_applications():
    query = db.select(Application).order_by(Application.id)
    status = request.args.get("status")
    if status is not None:
        if status not in STATUSES:
            return error("validation_failed", 422)
        query = query.where(Application.status == status)
    return jsonify({"data": [a.to_dict() for a in db.session.scalars(query)]})


@bp.get("/<int:application_id>")
def get_application(application_id: int):
    application = db.session.get(Application, application_id)
    if application is None:
        return error("not_found", 404)
    return jsonify({"data": application.to_dict()})


@bp.patch("/<int:application_id>/status")
def change_status(application_id: int):
    if not authorized():
        return error("unauthorized", 401)
    application = db.session.get(Application, application_id)
    if application is None:
        return error("not_found", 404)
    body = request.get_json(silent=True)
    target = body.get("status") if isinstance(body, dict) else None
    if target not in STATUSES:
        return error("validation_failed", 422)
    if target not in NEXT.get(application.status, set()):
        return error("invalid_transition", 409)
    application.status = target
    db.session.commit()
    return jsonify({"data": application.to_dict()})


@bp.delete("/<int:application_id>")
def delete_application(application_id: int):
    if not authorized():
        return error("unauthorized", 401)
    application = db.session.get(Application, application_id)
    if application is None:
        return error("not_found", 404)
    db.session.delete(application)
    db.session.commit()
    return "", 204

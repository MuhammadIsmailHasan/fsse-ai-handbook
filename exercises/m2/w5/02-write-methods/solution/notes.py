"""Reference solution."""

import hashlib
import json

from flask import Blueprint, request
from sqlalchemy import select

from app import ApiError
from models import IdempotencyRecord, Note, db

notes_bp = Blueprint("notes", __name__, url_prefix="/api/v1/notes")

EDITABLE = {"title", "body", "pinned"}
READ_ONLY = {"id", "user_id", "created_at", "updated_at"}


def current_user_id() -> int:
    raw = request.headers.get("X-User-Id", "")
    if not raw.isdigit():
        raise ApiError(401, "unauthorized", "Missing or invalid X-User-Id")
    return int(raw)


def json_object() -> dict:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ApiError(400, "invalid_json", "Body must be a JSON object")
    return data


def serialize(note: Note) -> dict:
    return {"id": note.id, "title": note.title, "body": note.body, "pinned": note.pinned}


def validate(data: dict, *, partial: bool) -> dict:
    """Return cleaned editable fields present in `data`; raise with ALL field errors."""
    errors: dict[str, str] = {}
    cleaned: dict = {}
    for name in data:
        if name in READ_ONLY:
            errors[name] = "read-only field"
        elif name not in EDITABLE:
            errors[name] = "unknown field"

    if "title" in data:
        title = data["title"]
        if title is None:
            errors["title"] = "cannot be null"
        elif not isinstance(title, str) or not 1 <= len(title.strip()) <= 120:
            errors["title"] = "must be 1-120 characters"
        else:
            cleaned["title"] = title.strip()
    elif not partial:
        errors["title"] = "required"

    if "body" in data:
        if data["body"] is not None and not isinstance(data["body"], str):
            errors["body"] = "must be a string or null"
        else:
            cleaned["body"] = data["body"]

    if "pinned" in data:
        if not isinstance(data["pinned"], bool):
            errors["pinned"] = "must be a boolean"
        else:
            cleaned["pinned"] = data["pinned"]

    if errors:
        raise ApiError(422, "validation_failed", "Invalid note", errors)
    return cleaned


def owned_note(note_id: int, user_id: int) -> Note:
    note = db.session.scalars(select(Note).where(Note.id == note_id, Note.user_id == user_id)).one_or_none()
    if note is None:
        raise ApiError(404, "note_not_found", f"Note {note_id} not found")
    return note


def location(note_id: int) -> dict:
    return {"Location": f"/api/v1/notes/{note_id}"}


@notes_bp.post("")
def create_note():
    user_id = current_user_id()
    data = json_object()
    key = request.headers.get("Idempotency-Key")
    request_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    if key is not None:
        if not 1 <= len(key) <= 100:
            raise ApiError(422, "validation_failed", "Invalid Idempotency-Key", {"Idempotency-Key": "1-100 characters"})
        existing = db.session.scalars(
            select(IdempotencyRecord).where(IdempotencyRecord.user_id == user_id, IdempotencyRecord.key == key)
        ).one_or_none()
        if existing is not None:
            if existing.request_hash != request_hash:
                raise ApiError(422, "idempotency_key_reused", "This Idempotency-Key was used with a different request")
            stored = existing.response_json
            return stored, existing.status_code, location(stored["data"]["id"])

    cleaned = validate(data, partial=False)  # validation failures never store the key
    note = Note(user_id=user_id, title=cleaned["title"], body=cleaned.get("body"), pinned=cleaned.get("pinned", False))
    db.session.add(note)
    db.session.flush()  # get note.id

    response = {"data": serialize(note)}
    if key is not None:
        db.session.add(
            IdempotencyRecord(user_id=user_id, key=key, request_hash=request_hash, status_code=201, response_json=response)
        )
    db.session.commit()  # note + idempotency record together
    return response, 201, location(note.id)


@notes_bp.get("/<int:note_id>")
def get_note(note_id: int):
    return {"data": serialize(owned_note(note_id, current_user_id()))}


@notes_bp.put("/<int:note_id>")
def replace_note(note_id: int):
    note = owned_note(note_id, current_user_id())
    cleaned = validate(json_object(), partial=False)
    note.title = cleaned["title"]
    note.body = cleaned.get("body")          # missing → reset to default
    note.pinned = cleaned.get("pinned", False)
    db.session.commit()
    return {"data": serialize(note)}


@notes_bp.patch("/<int:note_id>")
def patch_note(note_id: int):
    note = owned_note(note_id, current_user_id())
    data = json_object()
    if not data:
        raise ApiError(422, "no_fields", "Send at least one field to update")
    for field, value in validate(data, partial=True).items():   # only present fields change
        setattr(note, field, value)
    db.session.commit()
    return {"data": serialize(note)}


@notes_bp.delete("/<int:note_id>")
def delete_note(note_id: int):
    note = owned_note(note_id, current_user_id())
    db.session.delete(note)
    db.session.commit()
    return "", 204

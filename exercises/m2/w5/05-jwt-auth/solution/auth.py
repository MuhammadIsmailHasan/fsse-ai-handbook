"""Reference solution."""

import re
from datetime import UTC, datetime

from flask import Blueprint, Flask, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    current_user,
    get_jwt,
    jwt_required,
)
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app import ApiError
from models import RevokedToken, User, db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

ACCESS_EXPIRES_IN = 900
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
# Checked when the email is unknown, so both login failures take a similar amount of time.
DUMMY_HASH = generate_password_hash("not-a-real-password-just-for-timing")


def error(code: str, message: str):
    return {"error": {"code": code, "message": message}}, 401


def init_auth(app: Flask) -> None:
    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def missing_token(reason):
        return error("token_missing", reason)

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return error("token_expired", "Token has expired")

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return error("token_invalid", "Invalid token")

    @jwt.revoked_token_loader
    def revoked_token(jwt_header, jwt_payload):
        return error("token_revoked", "Token has been revoked")

    @jwt.token_in_blocklist_loader
    def is_revoked(jwt_header, jwt_payload) -> bool:
        return db.session.scalar(select(RevokedToken.id).where(RevokedToken.jti == jwt_payload["jti"])) is not None

    @jwt.user_lookup_loader
    def load_user(jwt_header, jwt_payload):
        return db.session.get(User, int(jwt_payload["sub"]))

    @jwt.user_lookup_error_loader
    def user_not_found(jwt_header, jwt_payload):
        return error("user_not_found", "User no longer exists")


def serialize(user: User) -> dict:
    return {"id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role}


def json_body() -> dict:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ApiError(422, "validation_failed", "Invalid body", {"body": "must be a JSON object"})
    return data


@auth_bp.post("/register")
def register():
    data = json_body()
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password")
    full_name = str(data.get("full_name", "")).strip()

    errors = {}
    if not EMAIL_PATTERN.match(email):
        errors["email"] = "must be a valid email address"
    if not isinstance(password, str) or len(password) < 12:
        errors["password"] = "must be at least 12 characters"
    if not 1 <= len(full_name) <= 100:
        errors["full_name"] = "must be 1-100 characters"
    if errors:
        raise ApiError(422, "validation_failed", "Some fields are invalid", errors)

    user = User(email=email, password_hash=generate_password_hash(password), full_name=full_name)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ApiError(409, "email_taken", "An account with this email already exists") from None
    return {"data": serialize(user)}, 201


@auth_bp.post("/login")
def login():
    data = json_body()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    user = db.session.scalars(select(User).where(func.lower(User.email) == email)).one_or_none()

    password_ok = check_password_hash(user.password_hash if user else DUMMY_HASH, password)
    if user is None or not password_ok:
        raise ApiError(401, "invalid_credentials", "Invalid email or password")

    return {
        "access_token": create_access_token(identity=str(user.id), additional_claims={"role": user.role}),
        "refresh_token": create_refresh_token(identity=str(user.id)),
        "token_type": "Bearer",
        "expires_in": ACCESS_EXPIRES_IN,
    }


@auth_bp.get("/me")
@jwt_required()
def me():
    return {"data": serialize(current_user)}


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    return {
        "access_token": create_access_token(identity=str(current_user.id), additional_claims={"role": current_user.role}),
        "token_type": "Bearer",
        "expires_in": ACCESS_EXPIRES_IN,
    }


def revoke_current_token() -> None:
    claims = get_jwt()
    db.session.add(
        RevokedToken(
            jti=claims["jti"],
            token_type=claims["type"],
            user_id=int(claims["sub"]),
            expires_at=datetime.fromtimestamp(claims["exp"], UTC),  # lets a cleanup job delete old rows
        )
    )
    db.session.commit()


@auth_bp.post("/logout")
@jwt_required()
def logout():
    revoke_current_token()
    return "", 204


@auth_bp.post("/logout-refresh")
@jwt_required(refresh=True)
def logout_refresh():
    revoke_current_token()
    return "", 204

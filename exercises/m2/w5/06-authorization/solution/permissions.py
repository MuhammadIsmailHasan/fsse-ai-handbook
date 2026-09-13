"""Reference solution."""

import functools

from flask_jwt_extended import current_user, jwt_required
from sqlalchemy import Select, select

from app import ApiError
from models import Application, User

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "user": frozenset({"applications:read_own", "applications:write_own"}),
    "mentor": frozenset({"applications:read_shared"}),
    "admin": frozenset({"applications:read_any", "applications:delete_any", "users:list"}),
}


def has_permission(role: str, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, frozenset())  # deny by default


def require_permission(permission: str):
    def decorator(view):
        @functools.wraps(view)
        @jwt_required()  # 401 for missing/invalid/expired tokens
        def wrapper(*args, **kwargs):
            # current_user comes from the database, so role changes apply immediately
            if not has_permission(current_user.role, permission):
                raise ApiError(403, "forbidden", "You don't have permission to do this")
            return view(*args, **kwargs)

        return wrapper

    return decorator


def can_view(user: User, application: Application) -> bool:
    return (
        application.user_id == user.id
        or (has_permission(user.role, "applications:read_shared") and application.shared_with_mentor_id == user.id)
        or has_permission(user.role, "applications:read_any")
    )


def can_edit(user: User, application: Application) -> bool:
    return application.user_id == user.id


def can_delete(user: User, application: Application) -> bool:
    return application.user_id == user.id or has_permission(user.role, "applications:delete_any")


def visible_applications_query(user: User) -> Select:
    stmt = select(Application)
    if has_permission(user.role, "applications:read_any"):
        return stmt
    if has_permission(user.role, "applications:read_shared"):
        return stmt.where(Application.shared_with_mentor_id == user.id)
    return stmt.where(Application.user_id == user.id)

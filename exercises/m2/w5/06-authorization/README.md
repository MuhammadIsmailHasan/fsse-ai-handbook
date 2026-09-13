# M2 · W5 · 06 — Roles, Permissions and Ownership

> 🚫🤖 **No-AI** · ⏱️ ~90 min · needs the exercise database (`docker compose up -d`)

Provided: `app.py` (factory, JWT setup with JSON 401 errors, `user_lookup_loader` so `current_user` is the **database** user, `ApiError` handler, registers `applications.applications_bp` and `applications.admin_bp`) and `models.py` (`User` with `role`; `Application` with `user_id` and `shared_with_mentor_id`).

## `permissions.py`
| Name | Behavior |
|---|---|
| `ROLE_PERMISSIONS` | `user`: `applications:read_own`, `applications:write_own` · `mentor`: `applications:read_shared` · `admin`: `applications:read_any`, `applications:delete_any`, `users:list` |
| `has_permission(role, permission)` | bool; unknown roles have none |
| `require_permission(permission)` | decorator: requires a valid access token (401 via JWT errors) and the permission for `current_user.role`, else `ApiError(403, "forbidden", …)`; keeps the view's name (`functools.wraps`) |
| `can_view(user, application)` | owner · mentor it's shared with · any user with `applications:read_any` |
| `can_edit(user, application)` | owner only |
| `visible_applications_query(user)` | a `select(Application)` filtered to what `user` may see (admin: all · mentor: shared with them · user: own) |

## `applications.py`
Application JSON: `{"id", "user_id", "company", "status"}`.

| Endpoint | Rules |
|---|---|
| `GET /api/v1/applications` | any authenticated user; returns `visible_applications_query(current_user)` ordered by `id` |
| `GET /api/v1/applications/<id>` | not found **or** not visible → `404 application_not_found` |
| `PATCH /api/v1/applications/<id>` `{"status"}` | not visible → 404; visible but not editable → `403 forbidden`; else update → 200 |
| `DELETE /api/v1/applications/<id>` | owner **or** `applications:delete_any` → 204; visible but not allowed → 403; not visible → 404 |
| `GET /api/v1/admin/users` | `@require_permission("users:list")` → `{"data": [{"id", "email", "role"}]}` ordered by id |

```bash
cd exercises
uv run pytest m2/w5/06-authorization
```

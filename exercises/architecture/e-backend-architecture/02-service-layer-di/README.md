# Architecture · E · Service Layer, Dependency Injection and a Thin API

> 🚫🤖 **No-AI** · ⏱️ ~90 min · no database needed

Provided (read them first):
- `domain.py` — `Application` with `move_to(new_status)` and the domain errors `InvalidTransition`
- `ports.py` — the protocols the service depends on (`UnitOfWork`, `EventPublisher`, `Clock`)
- `adapters.py` — `InMemoryUnitOfWork`, `LoggingPublisher`, `system_clock`

## 1. `services.py` — use cases
Errors: `ValidationFailed(field)`, `LimitReached`, `ApplicationNotFound` (define them here).

`ApplicationService(uow, publisher, clock, max_active_free=3)`:

| Method | Behavior |
|---|---|
| `add_application(user_id, plan, company, role)` | trims; blank `company` → `ValidationFailed("company")`, blank `role` → `ValidationFailed("role")`; on the `"free"` plan, if the user already has `max_active_free` **active** applications (`Application.is_active`) → `LimitReached`; otherwise add (with `created_at = updated_at = clock()`), **commit**, then publish `("application_added", {"application_id", "user_id"})`. Returns the DTO |
| `move(user_id, application_id, new_status)` | missing or another user's application → `ApplicationNotFound`; `application.move_to(new_status)` (may raise `InvalidTransition`); `updated_at = clock()`; **commit**, then publish `("application_status_changed", {"application_id", "user_id", "from", "to"})`. Returns the DTO |
| `list_applications(user_id)` | DTOs ordered by id |

DTO = plain dict `{"id", "company", "role", "status", "updated_at"}` with `updated_at` as an ISO string. Never return domain objects.
Events are published **only after a successful commit**; failures publish nothing and commit nothing.

## 2. `bootstrap.py` — composition root
`Container` dataclass with `applications: ApplicationService`. `bootstrap(uow=None, publisher=None, clock=None, max_active_free=3) -> Container` uses the adapters as defaults and the given objects otherwise. This is the **only** module that imports `adapters`.

## 3. `api.py` — a thin Flask adapter
`create_app(container) -> Flask`:
- `POST /users/<user_id>/applications` body `{"company", "role", "plan"}` → `201` DTO
- `POST /users/<user_id>/applications/<application_id>/status` body `{"status"}` → `200` DTO
- `GET /users/<user_id>/applications` → `200 {"data": [DTOs]}`
- errors → JSON `{"error": {"code": ...}}`: `ValidationFailed` `422 validation_failed` (+ `"field"`), `LimitReached` `403 limit_reached`, `ApplicationNotFound` `404 not_found`, `InvalidTransition` `409 invalid_transition`

Routes only translate HTTP ⇄ service calls: `api.py` must not import `adapters`, `domain.Application` or touch `uow` (a test checks).

```bash
cd exercises
uv run pytest architecture/e-backend-architecture/02-service-layer-di
```

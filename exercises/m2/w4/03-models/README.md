# M2 · W4 · 03 — Typed Models That Enforce the Rules

> 🚫🤖 **No-AI** · ⏱️ ~60 min · needs the exercise database (`docker compose up -d`)

Write `models.py` exposing `db` (Flask-SQLAlchemy with a `DeclarativeBase` subclass), plus the models below, in **SQLAlchemy 2.0 typed style** (`Mapped`, `mapped_column`).

### Naming convention (on the base's `MetaData`)
`"uq": "uq_%(table_name)s_%(column_0_name)s"`, `"ck": "ck_%(table_name)s_%(constraint_name)s"`, `"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"`, `"pk": "pk_%(table_name)s"`, `"ix": "ix_%(column_0_label)s"`

### `User` → table `users`
- `id` int PK · `email` string(320) required, **unique ignoring case** (index named `ix_users_email_lower`) · `full_name` string(200) required · `created_at` timezone-aware, server default now

### `Company` → table `companies`
- `id` · `name` string(200) required, unique · `website` string(500) optional · `created_at` as above

### `Application` → table `applications`
- `id` · `user_id` → `users.id` (ON DELETE CASCADE), required · `company_id` → `companies.id` (ON DELETE RESTRICT), required
- `role_title` string(200) required, check named `role_title_not_blank`: `length(trim(role_title)) > 0`
- `status`: `ApplicationStatus` StrEnum (`wishlist, applied, interview, offer, rejected, withdrawn`), stored as the lowercase value in a non-native enum **with a CHECK constraint** (`create_constraint=True`), Python default `APPLIED`, server default `'applied'`
- `salary_expectation` BigInteger optional, check named `salary_non_negative`: `salary_expectation >= 0`
- `created_at`, `updated_at` timezone-aware, server default now; `updated_at` also `onupdate=func.now()`
- unique constraint named `uq_applications_user_company_role` on `(user_id, company_id, role_title)`
- index named `ix_applications_user_created` on `(user_id, created_at)`
- `__repr__` → `<Application id=1 'Data Analyst' status=applied>`
- property `is_active` → `True` for applied/interview

```bash
cd exercises
uv run pytest m2/w4/03-models
```

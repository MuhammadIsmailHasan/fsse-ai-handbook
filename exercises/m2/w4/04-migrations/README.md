# M2 · W4 · 04 — A Safe Data Migration

> 🚫🤖 **No-AI** · ⏱️ ~60 min · needs the exercise database (`docker compose up -d`)

Production already runs migration **`0001`** (`migrations/versions/0001_create_applications.py`), which made two mistakes:
- `status` is nullable with no default
- salaries are stored as text: `salary_range = "9000000-14000000"`

Write migration **`0002`** in `migrations/versions/0002_split_salary_range.py` (`revision = "0002"`, `down_revision = "0001"`) that brings the table to the shape in `models.py`, **without losing data**.

### `upgrade()`
1. Add `salary_min` and `salary_max` (`BigInteger`, nullable)
2. **Backfill** them from `salary_range` when it matches `digits-digits` (e.g. `"9000000-14000000"`); anything else (e.g. `"negotiable"`, `NULL`) leaves both `NULL`
3. Set `status = 'applied'` where it is `NULL`, then make `status` **NOT NULL** with server default `'applied'`
4. Add check constraint **`ck_applications_salary_range_valid`**: `salary_min <= salary_max`
   ⚠️ `env.py` uses the models' metadata, which has a naming convention (`ck_%(table_name)s_%(constraint_name)s`). Find out what name you must pass so the **final** name is exactly `ck_applications_salary_range_valid` — and how `op.f()` helps when dropping it.
5. Drop `salary_range`

### `downgrade()`
Restore the `0001` shape: re-create `salary_range` filled as `"min-max"` where both values exist, drop the constraint, make `status` nullable without default, drop the new columns.

### Try it by hand (optional)
```bash
cd exercises/m2/w4/04-migrations
export DATABASE_URL=postgresql+psycopg://fsse:fsse@localhost:5491/fsse
uv run flask --app "app:create_app('$DATABASE_URL')" db upgrade      # careful: uses the public schema
uv run flask --app "app:create_app('$DATABASE_URL')" db downgrade 0001
```

### Run the tests
```bash
cd exercises
uv run pytest m2/w4/04-migrations
```

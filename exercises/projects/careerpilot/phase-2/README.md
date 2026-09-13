# CareerPilot · Phase 2 Starter Kit (Flask API)

Copy this folder into your repo as `careerpilot/api/`. Full brief: **Projects → CareerPilot → Phase 2** in the handbook.

```text
api/
├── careerpilot_api/__init__.py   ← create_app() stub — your code goes in this package
├── tests/
│   ├── conftest.py               ← fixtures (fresh schema + your migrations per test) — don't edit
│   └── acceptance/               ← 113 acceptance tests — don't edit
├── pyproject.toml                ← dependencies (uv)
├── compose.yaml                  ← local PostgreSQL on port 5492
└── .env.example
```

You will create: `migrations/` (`flask --app careerpilot_api db init`), your models, schemas, services, routes, `wsgi.py`, `gunicorn.conf.py`, `Dockerfile`, `.github/workflows/ci.yml`, a `locustfile.py` and a great README.

## Run the acceptance tests

In the handbook (uses the exercise database on 5491):

```bash
cd exercises
uv run pytest projects/careerpilot/phase-2 -x
uv run pytest projects/careerpilot/phase-2 -k auth      # one checkpoint at a time
```

In your own repo:

```bash
cd api
docker compose up -d
cp .env.example .env
uv sync
TEST_DATABASE_URL=postgresql://careerpilot:careerpilot@localhost:5492/careerpilot uv run pytest -x
```

| Checkpoint | Test file |
|---|---|
| C1 Platform | `test_phase2_platform.py` |
| C2 Auth | `test_phase2_auth.py` |
| C3 Companies | `test_phase2_companies.py` |
| C4 Applications & pipeline | `test_phase2_applications.py` |
| C5 Notes & stats | `test_phase2_notes_stats.py` |

# CareerPilot · Phase 3 Starter Kit (FastAPI AI service)

Copy this folder into your repo as `careerpilot/ai-service/`. Full brief: **Projects → CareerPilot → Phase 3** in the handbook.

```text
ai-service/
├── careerpilot_ai/
│   ├── __init__.py       ← create_app() stub — your app factory goes here
│   ├── skills.py         ← the skill vocabulary (given)
│   ├── matching.py       ← stub: extract_skills(), compare(), NoSkillsFound   (C3)
│   └── deps.py           ← stub: get_feedback_client(), get_audit_log()       (C4, C5)
├── tests/
│   ├── conftest.py       ← fixtures — don't edit
│   ├── p3_support.py     ← fakes and token helper — don't edit
│   └── acceptance/       ← 70 acceptance tests — don't edit
├── pyproject.toml        ← dependencies (uv)
└── .env.example
```

You will add: routers, schemas, services, settings, a `Dockerfile`, CI, your own unit tests and a great README. The tests only fix the **names above** and the **HTTP contract**; how you organise the rest is your design (see Module 3 W3 lesson 02).

No API key and no database are needed. The AI client and the audit log are *dependencies*, and the tests replace them with fakes (`app.dependency_overrides`).

## Run the acceptance tests

In the handbook:

```bash
cd exercises
uv run pytest projects/careerpilot/phase-3 -x
uv run pytest projects/careerpilot/phase-3 -k matching     # one checkpoint at a time
```

In your own repo:

```bash
cd ai-service
cp .env.example .env
uv sync
uv run pytest -x
uv run uvicorn --factory careerpilot_ai:create_app --env-file .env --port 5093 --reload
```

| Checkpoint | Test file |
|---|---|
| C1 Platform | `test_phase3_platform.py` |
| C2 Auth | `test_phase3_auth.py` |
| C3 Matching | `test_phase3_matching.py` |
| C4 `POST /v1/match` | `test_phase3_match_api.py` |
| C5 `POST /v1/feedback` (SSE) | `test_phase3_feedback.py` |

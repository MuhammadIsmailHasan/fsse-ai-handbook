# M2 · W4 · 05 — Relationships Without N+1

> 🚫🤖 **No-AI** · ⏱️ ~60 min · needs the exercise database (`docker compose up -d`)

`models.py` defines the columns and foreign keys. Add the **relationships** (typed `Mapped[...]`):

| Attribute | Kind | Notes |
|---|---|---|
| `Company.applications` ↔ `Application.company` | one-to-many | `back_populates` |
| `Application.skills` ↔ `Skill.applications` | many-to-many | through `application_skills` |
| `Application.interviews` ↔ `Interview.application` | one-to-many, **owned** | `cascade="all, delete-orphan"`, `passive_deletes=True`; `Application.interviews` ordered by `starts_at` |

Then implement `dashboard(user_id)` in `queries.py`, returning a list (newest `created_at` first) of:

```python
{
    "id": 12,
    "role_title": "Data Analyst",
    "company": "Kopi Data",
    "skills": ["python", "sql"],          # sorted A→Z
    "next_interview": "2026-09-20T10:00:00+00:00" or None,   # earliest interview starting at/after `now`, ISO format
}
```

`dashboard(user_id, now)` must run **at most 3 SQL statements** in total, however many applications exist.

```bash
cd exercises
uv run pytest m2/w4/05-relationships
```

# Architecture · E · Ports & Adapters (Hexagonal) Refactor

> 🚫🤖 **No-AI** · ⏱️ ~90 min · no database needed

The `hexajobs` package **works**, but its dependencies point the wrong way: the domain reads files and imports an adapter, and use cases build their own infrastructure. Refactor it — keep the same files — so that:

```text
entrypoints ──▶ adapters ──▶ application (use cases + ports) ──▶ domain
      └───────────────────────────────▲
```

| Layer | May import (inside `hexajobs`) | Must not import |
|---|---|---|
| `domain/` | only `hexajobs.domain` | anything else, plus no I/O modules (`json`, `os`, `pathlib`, `sys`, `io`, `sqlite3`, `requests`, `flask`, `sqlalchemy`) |
| `application/` | `hexajobs.domain`, `hexajobs.application` | adapters, entrypoints, I/O modules |
| `adapters/` | `hexajobs.domain`, `hexajobs.application` | entrypoints |
| `entrypoints/` | anything | — |

Contracts after the refactor:

| Where | What |
|---|---|
| `domain/model.py` | `JobPosting(id, title, company, salary_max, skills: tuple[str, ...])` (frozen) and `match_score(job, my_skills) -> float` (share of the job's skills I have, case-insensitive; `0.0` if the job lists none) |
| `application/ports.py` | `typing.Protocol`s: `JobFeed.fetch_jobs() -> list[JobPosting]`, `JobStore.save_all(jobs)` and `JobStore.all() -> list[JobPosting]`, `Notifier.notify(email, jobs)` |
| `application/use_cases.py` | `ImportJobs(feed, store)()` → saves only jobs whose `id` isn't stored yet, returns how many were new. `RecommendJobs(store, notifier)(email, my_skills, threshold=0.5)` → stored jobs with `match_score >= threshold`, sorted by score high → low then `id`; calls `notifier.notify(email, jobs)` only if the list isn't empty; returns the list |
| `adapters/json_feed.py` | `JsonFileFeed(path)` reads a JSON list of `{"id", "title", "company", "salary_max"?, "skills"}` (skills lower-cased) |
| `adapters/memory_store.py` | `InMemoryJobStore` keeps insertion order |
| `adapters/console_notifier.py` | `ConsoleNotifier(stream)` writes `To {email}: {n} job(s)` then `- {title} at {company}` per job, one line each |
| `entrypoints/cli.py` | `main(argv, stream)`: `recommend --feed PATH --email EMAIL --skills a,b [--threshold 0.5]` — wires the adapters (the **composition root**), prints `Imported {n} jobs`, runs the recommendation, returns `0` |

```bash
cd exercises
uv run pytest architecture/e-backend-architecture/03-hexagonal
```

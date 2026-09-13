# Architecture · D · Strategy, Observer and Command

> 🚫🤖 **No-AI** · ⏱️ ~75 min · everything in **`behaviors.py`**

## 1. Strategy — ranking jobs
Jobs are dicts: `{"id": str, "salary_max": int | None, "posted_on": date, "skills": list[str]}`.

| Piece | Contract |
|---|---|
| `BySalary()` | `score(job)` = `salary_max` or `0` |
| `ByRecency(today)` | `score(job)` = `-(today - posted_on).days` (newer = higher) |
| `BySkillMatch(my_skills)` | `score(job)` = fraction of the job's skills (case-insensitive) that I have; `0.0` if the job lists none |
| `rank_jobs(jobs, strategy)` | new list sorted by `strategy.score(job)` **high → low**, ties by `id` A → Z. Any object with `score` works |

## 2. Observer — an event bus
| Piece | Contract |
|---|---|
| `EventBus.subscribe(event_type, handler)` | registers `handler(payload)`; returns an `unsubscribe()` function |
| `EventBus.publish(event_type, payload)` | calls handlers for that type **in subscription order**; if a handler raises, log it with `logging.getLogger("events").exception(...)`, keep calling the others, and return the list of exceptions raised (empty if none) |

## 3. Command — undo/redo on an application board
`Board` (provided) holds `statuses: dict[int, str]` and `notes: dict[int, list[str]]`.

| Piece | Contract |
|---|---|
| `ChangeStatus(board, application_id, new_status)` | `execute()` sets the status (remembering the old one); `undo()` restores it |
| `AddNote(board, application_id, text)` | `execute()` appends the note; `undo()` removes that note |
| `History()` | `run(command)` executes and records it (and clears the redo stack); `undo()` / `redo()` return `True` if something happened, `False` if there was nothing to undo/redo |

```bash
cd exercises
uv run pytest architecture/d-design-patterns/03-strategy-observer-command
```

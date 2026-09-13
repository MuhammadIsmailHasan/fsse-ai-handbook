# M2 · W3 · 06 — An Application That Protects Its Rules

> 🚫🤖 **No-AI** · ⏱️ ~60 min

Implement in `pipeline.py`:

### `SalaryRange(minimum, maximum)` — immutable value object
- `ValueError` if `minimum < 0` or `maximum < minimum`
- `midpoint` property (integer, rounded down)
- equal when both values are equal; hashable; `repr` → `SalaryRange(9000000, 14000000)`

### `Application(company, role, applied_on, salary=None)`
- starts with status `"applied"`; `status` is a **read-only** property
- `history` → list of `(status, date)` tuples, starting with `("applied", applied_on)`; return a **copy** so callers can't mutate internal state
- `move_to(status, on)` — allowed transitions: `applied → interview | rejected | withdrawn`, `interview → interview | offer | rejected | withdrawn`, `offer → accepted | declined`; anything else raises `InvalidTransition`
- `is_active` property → `True` for `applied` and `interview`
- `repr` → `Application('Kopi Data', 'Data Analyst', status='applied')`
- sorting with `sorted()` orders by `applied_on` (implement `__lt__`)

### `ReminderService(notifier)`
- `send_follow_ups(applications, today, after_days=14)` → sends `notifier.send(message)` for each **active** application whose **last** status change is more than `after_days` days before `today`; message: `"Follow up with Kopi Data (Data Analyst)"`; returns the number sent

```bash
cd exercises
uv run pytest m2/w3/06-oop
```

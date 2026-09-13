# Architecture · A · Untangle the Reminder Job

> 🚫🤖 **No-AI** · ⏱️ ~45 min

Replace the tangled `run_reminders()` in `reminders.py` with a decoupled design:

| Function | Kind | Returns |
|---|---|---|
| `needs_follow_up(application, today, after_days=14)` | pure | `bool` — status `"applied"` and more than `after_days` days since `applied_on` |
| `build_message(application, today)` | pure | `"Follow up with {company} about {role} — applied {N} days ago."` |
| `send_follow_up_reminders(applications, today, notifier)` | coordinator | number sent; calls `notifier.send(email, message)` |
| `load_applications(path)` | I/O | list of dicts with `applied_on` converted to `date` |

```bash
cd exercises
uv run pytest architecture/a-principles/03-coupling-cohesion
```

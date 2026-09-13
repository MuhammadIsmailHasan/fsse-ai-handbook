# Architecture · A · Remove Duplicated Knowledge

> 🚫🤖 **No-AI** · ⏱️ ~30 min

Refactor `notifications.py`:
- greeting, date formatting and signature each defined **once**
- keep `follow_up_reminder`, `interview_reminder`, `deadline_reminder` with the same signatures
- all tests pass (one fails at the start — find out why)

Dates are always formatted like `Mon, 14 Sep 2026`.

```bash
cd exercises
uv run pytest architecture/a-principles/02-dry-kiss-yagni
```

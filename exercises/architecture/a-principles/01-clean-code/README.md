# Architecture · A · Refactor a Messy Report

> 🚫🤖 **No-AI** · ⏱️ ~45 min

The tests **already pass**. Your job: refactor `report.py` without breaking them.

Requirements (checked by tests):
- `status_report(applications, today)` keeps its name, parameters and output
- no function longer than **15 lines** (body)
- at least **4 functions** in the file
- no single-letter variable names except `_`

```bash
cd exercises
uv run pytest architecture/a-principles/01-clean-code
```

The structure tests fail at first — that's your target. The behavior tests must stay green the whole time.

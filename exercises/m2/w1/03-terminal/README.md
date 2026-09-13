# M2 · W1 · 03 — Log Detective Scripts

> 🚫🤖 **No-AI** · ⏱️ ~60 min · bash on macOS/Linux (Windows: use WSL or Git Bash)

## 1. `organize.sh DIR`

Move files **directly inside** `DIR` into subfolders (create them only when needed):

| Extension | Goes to |
|---|---|
| `.log` | `DIR/logs/` |
| `.csv`, `.json` | `DIR/data/` |
| `.png`, `.jpg` | `DIR/images/` |

Other files stay where they are. Print one summary line: `Moved 5 file(s)`.
Missing or non-directory argument → print `Error: not a directory: DIR` to stderr, exit `1`. No argument → usage message to stderr, exit non-zero.
File names may contain **spaces**.

## 2. `error_report.sh LOG_FILE`

Log lines look like: `2026-09-13T10:02:12 ERROR POST /api/applications 500 120ms`

Print exactly:

```text
Errors: 4
Top failing endpoints:
3 POST /api/applications
1 GET /api/jobs
```

- "Errors" counts lines with the level `ERROR`
- "Top failing endpoints" = method + path of `ERROR` lines, counted, most frequent first, **at most 3**; ties sorted alphabetically
- Missing file → `Error: file not found: LOG_FILE` to stderr, exit `1`

## Run the tests

```bash
cd exercises
uv run pytest m2/w1/03-terminal
```

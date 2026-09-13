# Architecture · D · State and Template Method

> 🚫🤖 **No-AI** · ⏱️ ~60 min · everything in **`workflow.py`**

## 1. State — an application's lifecycle
`ApplicationWorkflow()` starts in the **saved** state. Actions: `apply()`, `schedule_interview()`, `make_offer(amount)`, `accept()`, `reject()`, `withdraw()`.

| State (`workflow.status`) | Allowed actions → next state |
|---|---|
| `saved` | `apply` → `applied`; `withdraw` → `withdrawn` |
| `applied` | `schedule_interview` → `interviewing`; `reject` → `rejected`; `withdraw` → `withdrawn` |
| `interviewing` | `schedule_interview` → `interviewing` (another round); `make_offer(amount)` → `offered`; `reject`; `withdraw` |
| `offered` | `accept` → `accepted`; `reject`; `withdraw` |
| `accepted`, `rejected`, `withdrawn` | nothing |

- Any other action raises `InvalidAction(f"cannot {action} when {status}")` — e.g. `"cannot accept when applied"`, and the state doesn't change
- `workflow.interview_rounds` counts scheduled interviews; `workflow.offer_amount` stores the offer (`None` before)
- `workflow.history` lists statuses visited, starting with `["saved"]`
- Implement each state as its **own class** (`Saved`, `Applied`, …) that decides what its actions do. `ApplicationWorkflow` delegates to the current state object and must **not** compare status strings (a test checks for `if status == ...` style code in it)

## 2. Template Method — reports
`ApplicationReport` is a base class whose `generate(applications)` is the **template**: `header()` + one `row(app)` per application + `footer(applications)`, joined with `"\n"`.

| Hook | Base behavior |
|---|---|
| `title` (class attribute) | `"Applications"` |
| `header()` | **abstract** — subclasses must implement |
| `row(app)` | **abstract** |
| `footer(applications)` | `f"Total: {len(applications)}"` |

- `PlainTextReport`: header `"== Applications =="`, row `"- {company}: {role} ({status})"`
- `MarkdownReport`: title `"Job Hunt"`, header `"# Job Hunt\n\n| Company | Role | Status |\n|---|---|---|"`, row `"| {company} | {role} | {status} |"`, footer `"\n_Total: N applications_"`
- Instantiating `ApplicationReport` directly raises `TypeError` (use `abc`)

```bash
cd exercises
uv run pytest architecture/d-design-patterns/04-state-template-method
```

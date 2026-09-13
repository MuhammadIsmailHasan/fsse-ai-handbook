# Architecture · C · Accounts by Composition

> 🚫🤖 **No-AI** · ⏱️ ~45 min

`legacy_accounts.py` models users with inheritance: `JobSeeker`, `Recruiter`, `ProJobSeeker`, `ProRecruiter`, … A user who is both a recruiter and a job seeker on a Pro plan needs yet another class, and upgrading a plan means **replacing the object**. Rebuild it with composition in **`accounts.py`**:

| Piece | Contract |
|---|---|
| `Role` | frozen dataclass `name: str`, `permissions: frozenset[str]` |
| `JOB_SEEKER`, `RECRUITER`, `ADMIN` | `Role("job_seeker", {"applications:read", "applications:write", "jobs:read"})`, `Role("recruiter", {"jobs:read", "jobs:write", "candidates:read"})`, `Role("admin", {"*"})` |
| `Plan` | frozen dataclass `name: str`, `features: frozenset[str]`, `limits: dict[str, int]` — a dict isn't hashable, so declare it with `field(default_factory=dict, hash=False, compare=False)` |
| `FREE`, `PRO` | `Plan("free", {"tracker"}, {"applications": 20})`, `Plan("pro", {"tracker", "ai_match", "export"}, {"applications": 1000})` |
| `Account(email, roles=None, plan=FREE)` | holds a **set** of roles and **one** plan |
| `grant(role)` / `revoke(role)` | change roles at runtime (revoking a role you don't have is fine) |
| `change_plan(plan)` | switch plans at runtime |
| `can(permission) -> bool` | true if any role has the exact permission, `"*"`, or a resource wildcard like `"jobs:*"` matching `"jobs:write"` |
| `has_feature(feature) -> bool` / `limit(name) -> int` | from the current plan (`0` for unknown limits) |

No class in `accounts.py` may inherit from another class (a test checks) — combine small objects instead.

```bash
cd exercises
uv run pytest architecture/c-oop-design/02-composition-accounts
```

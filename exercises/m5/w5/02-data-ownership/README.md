# M5 · W5 · 02 — Find broken data boundaries

> 🚫🤖 **No-AI** · ⏱️ ~30 min

Each service must be the **only** one that writes to the tables it owns. When another service writes to those tables, you have the shared-database trap. Detect it in `data_ownership.py`.

## Data

```python
@dataclass(frozen=True)
class Service:
    name: str
    owns: tuple[str, ...]    # tables this service owns
    writes: tuple[str, ...]  # tables this service writes to
```

Assume every owned table has exactly one owner.

## Function

```python
find_ownership_violations(services: list[Service]) -> list[str]
```

A **violation** is a service that writes to a table owned by a *different* service. For each one, add a message in this exact shape:

```
<writer> writes to <table> owned by <owner>
```

Rules:

- A service writing to a table it **owns** is fine — not a violation.
- A service writing to a table **nobody** owns is ignored (not a violation here).
- Return the messages **sorted** (so the output is stable).

Example: if `Orders` writes to `products`, and `Catalog` owns `products`, the result contains
`"Orders writes to products owned by Catalog"`.

```bash
cd exercises
uv run pytest m5/w5/02-data-ownership
```

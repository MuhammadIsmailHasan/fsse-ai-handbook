# M5 · W7 · 01 — Compute a Terraform plan

> 🚫🤖 **No-AI** · ⏱️ ~25 min

Terraform's core move is a diff: compare what exists now with what your code asks for, and show what will be **created**, **changed**, or **destroyed**. Build that diff in `terraform_plan.py`.

## Function

```python
plan(current: dict, desired: dict) -> dict
```

`current` and `desired` are both `{name: attributes}`, where `attributes` is a dict of that resource's settings. Compare them:

- **create** — a name in `desired` but not in `current`.
- **destroy** — a name in `current` but not in `desired`.
- **change** — a name in both, but whose attributes are not equal.
- A name in both with identical attributes is unchanged (in none of the lists).

Return `{"create": [...], "change": [...], "destroy": [...]}` with each list of names **sorted**.

Example:

```python
current = {"web": {"type": "t3.micro"}, "old": {"type": "t3.nano"}}
desired = {"web": {"type": "t3.small"}, "db": {"engine": "postgres"}}
plan(current, desired)
# -> {"create": ["db"], "change": ["web"], "destroy": ["old"]}
```

```bash
cd exercises
uv run pytest m5/w7/01-terraform-plan
```

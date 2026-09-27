# M5 · W6 · 01 — Write Kubernetes' control loop

> 🚫🤖 **No-AI** · ⏱️ ~20 min

The one idea behind Kubernetes: keep the number of running copies matching the number you asked for. Write that comparison in `reconcile.py`.

## Function

```python
reconcile(desired: int, actual: int) -> dict
```

Compare `desired` (how many copies you want) with `actual` (how many are running) and return the step to close the gap:

- `actual < desired` → start the missing pods: `{"action": "start", "count": desired - actual}`
- `actual > desired` → stop the extra pods: `{"action": "stop", "count": actual - desired}`
- `actual == desired` → nothing to do: `{"action": "none", "count": 0}`

Example:

```python
reconcile(3, 2)  # -> {"action": "start", "count": 1}   # one pod crashed; start a replacement
reconcile(3, 5)  # -> {"action": "stop", "count": 2}    # scaled down; remove two
reconcile(3, 3)  # -> {"action": "none", "count": 0}
```

```bash
cd exercises
uv run pytest m5/w6/01-reconcile
```

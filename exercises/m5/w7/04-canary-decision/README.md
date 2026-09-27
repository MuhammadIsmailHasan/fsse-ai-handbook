# M5 · W7 · 04 — Drive a canary rollout

> 🚫🤖 **No-AI** · ⏱️ ~20 min

A canary watches the new version's error rate and decides what to do next. Encode that control logic in `canary_decision.py`.

## Function

```python
canary_decision(error_rate: float, threshold: float, percent: int) -> str
```

`error_rate` is the new version's current error rate, `threshold` is the most you'll tolerate, and `percent` is how much traffic the canary currently gets (0–100). Return one of:

- `"rollback"` — if `error_rate > threshold` (unhealthy), no matter the percent. **Safety first.**
- `"done"` — healthy and already at 100% (`percent >= 100`).
- `"promote"` — healthy but not fully rolled out yet (send it more traffic).

Example:

```python
canary_decision(0.01, 0.05, 5)    # -> "promote"   # healthy, grow it
canary_decision(0.09, 0.05, 5)    # -> "rollback"  # too many errors
canary_decision(0.01, 0.05, 100)  # -> "done"      # healthy and fully out
```

```bash
cd exercises
uv run pytest m5/w7/04-canary-decision
```

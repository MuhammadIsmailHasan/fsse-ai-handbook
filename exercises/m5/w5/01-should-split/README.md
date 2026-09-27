# M5 · W5 · 01 — Decide whether to split a service

> 🚫🤖 **No-AI** · ⏱️ ~30 min

"Monolith first" means you split a piece into its own service only when there is **real evidence**, and never while you are still learning where the boundaries are. Encode that rule as a small function in `should_split.py`.

## Function

```python
should_extract_service(signals: dict) -> tuple[bool, list[str]]
```

`signals` is a dictionary of booleans. Return `(recommend_split, reasons)`.

**The guard (monolith first).** If `signals["still_finding_boundaries"]` is `True`, return:

```python
(False, ["monolith first: still finding the boundaries"])
```

…no matter what the other signals say.

**The real signals.** Otherwise, collect a reason for every signal below that is `True`, **in this exact order**:

| Signal key | Reason text |
|---|---|
| `different_scaling_needs` | `different scaling needs` |
| `separate_team_owns_it` | `a separate team owns it` |
| `different_release_cadence` | `different release speed` |
| `clear_data_boundary` | `a clear data boundary` |

**The decision.** Recommend the split (`True`) only when there are **at least two** reasons. With zero or one reason, return `False` — but still return the reasons you found, so the caller sees the evidence.

Missing keys count as `False` (use `signals.get(key)`).

```bash
cd exercises
uv run pytest m5/w5/01-should-split
```

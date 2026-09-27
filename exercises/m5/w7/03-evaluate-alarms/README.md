# M5 · W7 · 03 — Decide which alarms fire

> 🚫🤖 **No-AI** · ⏱️ ~25 min

An alarm is a rule on a metric. Given the current readings and a set of rules, decide which alarms are firing — the check CloudWatch runs every minute. Write it in `evaluate_alarms.py`.

## Data

```python
readings: dict[str, float]     # metric name -> current value, e.g. {"error_rate": 0.08, "cpu": 55}
rule: {"name": str, "metric": str, "op": str, "threshold": float}
#   op is one of ">", "<", ">=", "<="
```

## Function

```python
evaluate_alarms(readings: dict, rules: list[dict]) -> list[str]
```

For each rule, compare `readings[metric]` against `threshold` using `op`. Collect the `name` of every rule whose comparison is **True**. Rules:

- If the rule's `metric` isn't in `readings`, the alarm can't be evaluated — **skip it**.
- Return the firing names **sorted**.

Example:

```python
readings = {"error_rate": 0.08, "cpu": 55}
rules = [
    {"name": "high-errors", "metric": "error_rate", "op": ">", "threshold": 0.02},
    {"name": "high-cpu", "metric": "cpu", "op": ">", "threshold": 80},
]
evaluate_alarms(readings, rules)  # -> ["high-errors"]
```

```bash
cd exercises
uv run pytest m5/w7/03-evaluate-alarms
```

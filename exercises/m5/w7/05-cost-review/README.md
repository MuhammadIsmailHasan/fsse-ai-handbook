# M5 · W7 · 05 — Review costs and find waste

> 🚫🤖 **No-AI** · ⏱️ ~25 min

Every cost review starts with two questions: what does this cost per month, and what's running for nothing? Answer both in `cost_review.py`.

## Data

```python
@dataclass(frozen=True)
class Resource:
    name: str
    hourly_cost: float   # dollars per hour
    in_use: bool         # is anything actually using it?
```

Use **730 hours** as one month.

## Functions

```python
monthly_cost(resources: list[Resource]) -> float
```

Total monthly cost of **all** resources (in use or not): sum of `hourly_cost * 730`, rounded to 2 decimals.

```python
idle_resources(resources: list[Resource]) -> list[str]
```

The **sorted** names of resources where `in_use` is `False` — the orphans to clean up.

Example:

```python
res = [Resource("api", 0.10, True), Resource("old-db", 0.20, False)]
monthly_cost(res)    # -> 219.0     # (0.10 + 0.20) * 730
idle_resources(res)  # -> ["old-db"]
```

```bash
cd exercises
uv run pytest m5/w7/05-cost-review
```

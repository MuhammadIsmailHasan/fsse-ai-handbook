# M5 · W5 · 03 — Process each message exactly once

> 🚫🤖 **No-AI** · ⏱️ ~25 min

A queue delivers messages **at least once**, so the same message can arrive more than once. Your payment worker must charge each message only once. Make it idempotent in `idempotent_consumer.py`.

## Function

```python
apply_once(events: list[tuple[str, int]]) -> tuple[int, list[str]]
```

Each event is `(message_id, amount)`. Process the events **in order**:

- The first time you see a `message_id`, add its `amount` to the running total and record the id.
- If you see a `message_id` you've **already applied**, skip it — add nothing.

Return `(total, applied_ids)` where `applied_ids` is the list of ids you actually applied, in the order they were **first seen**.

Example:

```python
apply_once([("m1", 100), ("m2", 50), ("m1", 100)])
# -> (150, ["m1", "m2"])   # the second "m1" is a duplicate, ignored
```

```bash
cd exercises
uv run pytest m5/w5/03-idempotent-consumer
```

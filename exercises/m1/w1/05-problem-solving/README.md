# M1 · W1 · 05 — Free Interview Slots

> 🚫🤖 **No-AI** · ⏱️ ~60–90 min · Lesson: *Problem Solving Process*

**First** write your examples and pseudocode (lesson Part 2). **Then** implement `slots.py`:

| Function | Example | Result |
|---|---|---|
| `to_minutes(text)` | `"09:30"` | `570` |
| `to_text(minutes)` | `570` | `"09:30"` |
| `merge_ranges(ranges)` | `[(600, 720), (540, 660)]` | `[(540, 720)]` |
| `free_slots(busy, length, day_start="09:00", day_end="17:00")` | see below | list of `("HH:MM", "HH:MM")` |

Rules for `free_slots`:
- `busy` is a list of `("HH:MM", "HH:MM")` tuples — unsorted, may overlap, may extend outside the day
- End times are exclusive: busy until 10:30 means free from 10:30
- Ranges that touch (`10:00–11:00` and `11:00–12:00`) merge into one
- Return gaps inside the day that are **at least** `length` minutes, in time order

```python
free_slots([("13:00", "14:00"), ("09:00", "10:30")], 60)
# [("10:30", "13:00"), ("14:00", "17:00")]
```

```bash
cd exercises
uv run pytest m1/w1/05-problem-solving
```

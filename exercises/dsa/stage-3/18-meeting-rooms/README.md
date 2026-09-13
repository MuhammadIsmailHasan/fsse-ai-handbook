# DSA · Stage 3 · Interview Rooms Needed

> 🟡 Medium · 🚫🤖 No-AI · Target: O(n log n)

A company schedules interviews as `(start, end)` minute pairs. A room is free again **at** the end time (`(9, 10)` and `(10, 11)` can share a room).

`rooms_needed(interviews)` → the minimum number of rooms so no two interviews in the same room overlap.

```python
rooms_needed([(0, 30), (5, 10), (15, 20)])   # 2
rooms_needed([(7, 10), (2, 4)])              # 1
rooms_needed([])                             # 0
```

Two classic approaches: sort by start and keep a min-heap of end times, **or** sort all starts and all ends separately and sweep with two pointers.

```bash
cd exercises
uv run pytest dsa/stage-3/18-meeting-rooms
```

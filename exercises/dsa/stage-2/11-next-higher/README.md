# DSA · Stage 2 · Days Until a Higher Price

> 🟡 Medium · 🚫🤖 No-AI · Target: **O(n)** with a monotonic stack

A course platform tracks daily prices. For each day, how many days until the price is **strictly higher**? `0` if it never is.

```python
days_until_higher([73, 74, 75, 71, 69, 72, 76, 73])
# [1, 1, 4, 2, 1, 1, 0, 0]
```

The brute force (look ahead from every day) is O(n²). Keep a stack of **indices whose answer isn't known yet**; when a higher price arrives, it answers everyone on the stack it beats.

```bash
cd exercises
uv run pytest dsa/stage-2/11-next-higher
```

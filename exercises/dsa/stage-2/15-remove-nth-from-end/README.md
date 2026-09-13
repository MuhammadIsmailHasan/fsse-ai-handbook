# DSA · Stage 2 · Remove the N-th Item From the End

> 🟡 Medium · 🚫🤖 No-AI · Target: **one pass**, O(1) extra space

A notification feed is a singly linked list (newest first). Remove the `n`-th node **from the end** and return the head.

```python
remove_nth_from_end(1 → 2 → 3 → 4 → 5, n=2)   # 1 → 2 → 3 → 5
remove_nth_from_end(1, n=1)                   # None
```

- `1 <= n <= length`
- Hint: move a `lead` pointer `n` steps ahead, then move `lead` and `trail` together. A dummy node in front handles removing the head.
- Counting the length first and walking again also works (two passes, still O(L)). Do the one-pass version: it's what interviewers ask for, and it works when you can only traverse once.

```bash
cd exercises
uv run pytest dsa/stage-2/15-remove-nth-from-end
```

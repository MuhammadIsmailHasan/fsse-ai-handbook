# DSA · Stage 3 · Longest Run Without Repeats

> 🟡 Medium · 🚫🤖 No-AI · Target: O(n)

A session-replay tool looks for the longest stretch of clicks where no page repeats. With pages encoded as characters:

`longest_unique_run(text)` → the length of the longest substring with **no repeated characters**.

```python
longest_unique_run("abcabcbb")   # 3  ("abc")
longest_unique_run("pwwkew")     # 3  ("wke")
longest_unique_run("")           # 0
```

Variable-size window: grow the right edge; when a character repeats, move the left edge past its previous position (a dict `char → last index` lets you jump).

```bash
cd exercises
uv run pytest dsa/stage-3/06-longest-unique-substring
```

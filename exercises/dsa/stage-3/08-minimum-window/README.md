# DSA · Stage 3 · Shortest Snippet With All Keywords

> 🔴 Stretch · 🚫🤖 No-AI · Target: O(len(text) + len(required))

A search engine highlights the **shortest** snippet of a document that contains all required characters (with multiplicity).

`shortest_covering(text, required)` → the shortest substring of `text` containing every character of `required` at least as many times as it appears there. If several have the same length, return the **leftmost**. Return `""` if impossible or if `required` is empty.

```python
shortest_covering("ADOBECODEBANC", "ABC")   # "BANC"
shortest_covering("aa", "aa")               # "aa"
shortest_covering("a", "aa")                # ""
```

Expand right until the window is valid, then shrink left while it stays valid; track how many required characters are still **missing** so each check is O(1).

```bash
cd exercises
uv run pytest dsa/stage-3/08-minimum-window
```

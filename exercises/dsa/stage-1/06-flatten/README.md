# DSA · Stage 1 · Flatten Nested Lists

> 🟡 Medium

| Function | Example | Result |
|---|---|---|
| `flatten(items)` | `[1, [2, [3, 4]], [], 5]` | `[1, 2, 3, 4, 5]` |
| `max_depth(items)` | `[1, [2, [3]]]` | `3` |

`max_depth([])` is `1` (a list is depth 1 even when empty). Only `list` counts as nesting — strings are values.
Don't modify the input.

```bash
cd exercises
uv run pytest dsa/stage-1/06-flatten
```

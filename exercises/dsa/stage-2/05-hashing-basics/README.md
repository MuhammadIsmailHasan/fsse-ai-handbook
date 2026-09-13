# DSA · Stage 2 · Hashing Basics

> 🟢 Easy set · 🚫🤖 No-AI · Target: O(n) each

| Function | Example | Result |
|---|---|---|
| `first_repeat(items)` | `["js", "py", "go", "py", "js"]` | `"py"` — the first item whose value was **already seen**; `None` if no repeats |
| `is_anagram(a, b)` | `"listen", "silent"` | `True` — same letters, same counts (case-sensitive, spaces count) |
| `common_skills(mine, wanted)` | `["sql", "python", "sql"], ["python", "docker", "sql"]` | `["python", "sql"]` — items in **both**, unique, in the order they appear in `wanted` |

No `sorted()` / `.sort()` in `is_anagram` — count instead (a test checks).

```bash
cd exercises
uv run pytest dsa/stage-2/05-hashing-basics
```

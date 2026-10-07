# Module 3 · W3 · Check a Project Layout

> 🚫🤖 **No-AI** · ⏱️ ~35 min

A real FastAPI app has layers: `routers → services → repositories → models`. In `layout_rules.py` write the small checker a team could run in CI:

| Function | Does |
|---|---|
| `layer_of(module)` | `"app.routers.users"` → `"routers"` |
| `find_violations(imports)` | list `(importer, imported)` pairs that break the layer rules, sorted |
| `find_cycle(imports)` | return one circular import path like `["a", "b", "a"]`, or `None` |

The rules are written at the top of the file. Imports from outside `app.` (fastapi, sqlalchemy…) are ignored.

```bash
cd exercises
uv run pytest m3/w3/02-layout
```

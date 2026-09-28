# Architecture · F · Tiny GraphQL-Style Selector

> 🚫🤖 **No-AI** · ⏱️ ~30 min

Build the idea at the heart of GraphQL by hand: return only the fields the client asked for, and measure the over-fetching a REST-style "return everything" response causes.

A **selection** is a dict: `True` means "include this field", a nested dict means "recurse".

```python
graphql_select(user, {"name": True, "orders": {"total": True}})
# → {"name": "Ismail", "orders": [{"total": 100000}, {"total": 30000}]}
```

| Function | Does |
|---|---|
| `graphql_select(obj, selection)` | Return only the requested fields (nested + lists supported) |
| `count_leaves(obj)` | Count the actual field values carried |
| `over_fetch_count(full, selection)` | Extra leaves a full response sends vs a selected one |

```bash
cd exercises
uv run pytest architecture/f-data-api-design/04-graphql-select
```

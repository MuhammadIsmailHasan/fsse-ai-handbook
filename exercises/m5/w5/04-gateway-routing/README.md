# M5 · W5 · 04 — Route requests to the right backend

> 🚫🤖 **No-AI** · ⏱️ ~25 min

This is the heart of an API gateway: a routing table that forwards each request to the right service. Write it in `gateway_routing.py`.

## Function

```python
pick_backend(path: str, routes: list[tuple[str, str]]) -> str | None
```

Each route is `(prefix, backend)`. Return the backend to forward `path` to:

- A route **matches** when `path.startswith(prefix)`.
- Among all matching routes, return the backend of the one with the **longest** prefix (the most specific).
- If nothing matches, return `None`.

Example:

```python
routes = [("/orders", "orders-svc"), ("/orders/history", "orders-history-svc"), ("/products", "catalog-svc")]
pick_backend("/orders/history/42", routes)  # -> "orders-history-svc"  (longest match)
pick_backend("/orders/42", routes)          # -> "orders-svc"
pick_backend("/unknown", routes)            # -> None
```

```bash
cd exercises
uv run pytest m5/w5/04-gateway-routing
```

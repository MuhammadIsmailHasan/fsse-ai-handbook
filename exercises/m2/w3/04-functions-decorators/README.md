# M2 · W3 · 04 — Build Your Own Decorators

> 🚫🤖 **No-AI** · ⏱️ ~60 min

Implement in `decorators.py`:

### `timed(records, clock=time.perf_counter)`
Decorator **factory**. Each call to the decorated function appends `(function_name, elapsed_seconds)` to `records` — even if the function raises (the exception must still propagate). Return values pass through.

### `retry(times, exceptions=(Exception,))`
Decorator factory. Call the function up to `times` attempts; retry **only** on the given exception types; after the last failed attempt, re-raise that exception. Other exceptions propagate immediately. `times < 1` → `ValueError` when creating the decorator.

### `make_rate_limiter(max_calls, per_seconds, clock=time.monotonic)`
Returns a function `allow() -> bool`: `True` if fewer than `max_calls` were allowed in the last `per_seconds` seconds (sliding window), else `False`. Uses a **closure** (no classes, no globals).

### `Router`
- `route(method, path)` → decorator that registers the function and returns it **unchanged**
- `dispatch(method, path, *args, **kwargs)` → calls the handler; unknown route raises `LookupError`
- Registering the same method + path twice raises `ValueError`
- `method` is case-insensitive (`"get"` == `"GET"`)

All decorators that wrap must use `functools.wraps`.

```bash
cd exercises
uv run pytest m2/w3/04-functions-decorators
```

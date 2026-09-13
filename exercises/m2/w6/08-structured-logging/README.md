# M2 · W6 · 08 — Structured JSON Logging with Request IDs

> 🚫🤖 **No-AI** · ⏱️ ~75 min · no database needed

## Part 1 — `logging_setup.py`
- `request_id_var` (provided): a `ContextVar` holding the current request id (or `None`).
- `redact(value)` → a copy where any dict key containing `password`, `secret`, `token`, `authorization`, `api_key`, `apikey` or `cookie` (case-insensitive) has the value `"[REDACTED]"`. Recurse into dicts, lists and tuples (tuples come back as lists). Other values are returned unchanged.
- `JsonFormatter.format(record)` → **one line** of JSON:
  - `timestamp`: UTC from `record.created`, ISO 8601 with milliseconds and `Z` (`2026-01-01T00:00:00.500Z`)
  - `level`, `logger` (record name), `message` (`record.getMessage()`, so `%d` args work)
  - `request_id` only when `request_id_var` has a value
  - every field passed with `extra={...}`, run through `redact` (hint: compare `vars(record)` with the attributes of a plain `LogRecord`)
  - with exception info: `exc_type` (class name), `exc_message` (`str(exc)`), `stack` (full formatted traceback, inside the JSON string)
  - values JSON can't encode (dates, `Decimal`) become strings
- `configure_logging(level="INFO", stream=None)` → the **root** logger gets one `StreamHandler` (default `sys.stdout`) with `JsonFormatter`, and the given level (case-insensitive). Calling it again must **replace** its previous handler, not add a second one.

## Part 2 — `request_logging.py`
`init_request_logging(app)`:
- before each request: reuse `X-Request-ID` if it matches `^[A-Za-z0-9._-]{1,64}$`, otherwise generate `uuid.uuid4().hex`; set `request_id_var`
- after each request: add the `X-Request-ID` response header and log `"request completed"` on the `"http"` logger with extras `method`, `path` (**without** query string), `status`, `duration_ms` (number). Level: `INFO` for < 400, `WARNING` for 4xx, `ERROR` for 5xx
- at teardown: reset the context variable so the id doesn't leak into later work

```bash
cd exercises
uv run pytest m2/w6/08-structured-logging
```

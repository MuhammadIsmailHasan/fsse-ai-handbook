# M5 · W4 · 05 — Configuration from Parameter Store and Secrets Manager

> 🚫🤖 **No-AI** · ⏱️ ~90 min · AWS is mocked with **moto**

ECS can inject secrets into environment variables at task start. Sometimes an app (or a Lambda, or a CLI tool) must load configuration **itself** — with pagination, decryption, caching and safe refreshes. Write `config_loader.py`.

## 1. `load_parameters(ssm, path) -> dict[str, str]`
- `path` must start and end with `/` (e.g. `/revoshop/production/`) → else `ValueError`
- read **all** parameters under the path **recursively**, decrypted, following `NextToken` pagination (use a paginator or a loop — the test creates more than one page)
- key = name without the path prefix, `/` replaced by `_`, upper-cased: `/revoshop/production/midtrans/server_key` → `MIDTRANS_SERVER_KEY`
- resulting keys must match `^[A-Z][A-Z0-9_]*$` → else `ValueError`; two parameters mapping to the same key → `ValueError`

## 2. `resolve_references(config, secrets) -> dict[str, str]`
Values of the form `secretsmanager:<secret id>#<json key>` are replaced by that JSON key of the secret (RDS-managed secrets store `{"username", "password"}`). Other values stay as they are. A missing key → `KeyError`. Each secret is fetched **once** even when referenced several times.

## 3. `CachedConfig(load, *, ttl, max_stale, clock=time.monotonic)`
- `get() -> dict` returns the cached value while younger than `ttl` seconds; otherwise calls `load()`
- if a refresh raises and the cached value is younger than `max_stale` seconds → return the stale value (log a warning); older or no cache → re-raise
- `invalidate()` forces the next `get()` to reload

```bash
cd exercises
uv run pytest m5/w4/05-ssm-config-loader
```

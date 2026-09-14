# M5 · W2 · 03 — Environment parity checker

> 🚫🤖 **No-AI** · ⏱️ ~90 min

"It worked in staging" usually means staging and production **weren't configured the same way**. Write `env_parity.py`, a tool CI can run before a deploy to compare environment files **without ever printing a secret**.

## 1. `parse_env(text) -> dict[str, str]`
- skip blank lines and lines starting with `#`; allow an optional `export ` prefix
- `KEY=value` — keys match `[A-Za-z_][A-Za-z0-9_]*`; `KEY=` is an empty string
- unquoted values: trim spaces; ` #` starts an inline comment
- `'single quoted'` values are literal; `"double quoted"` values support `\n`, `\"` and `\\`; `#` inside quotes is not a comment
- anything else → `ValueError` mentioning the **line number** (`line 3`)

## 2. `check(environments, *, required) -> list[Issue]`
`environments` maps a name (`"staging"`, `"production"`) to a parsed dict. `Issue(environment, key, code, message)`, sorted by `(environment, key, code)`.

| Code | Report when |
|---|---|
| `MISSING` | a `required` key is absent or empty in an environment |
| `DRIFT` | a key exists (non-required) in some environments but not in this one |
| `DEBUG_IN_PRODUCTION` | in `production`, `DEBUG` or `FLASK_DEBUG` is truthy (`1`, `true`, `yes`, `on`, any case) |
| `LOCALHOST_IN_PRODUCTION` | in `production`, a value contains `localhost` or `127.0.0.1` |
| `SANDBOX_IN_PRODUCTION` | in `production`, `MIDTRANS_IS_PRODUCTION` isn't `true`, or any value starts with `SB-Mid-` |
| `WEAK_SECRET` | in `staging` or `production`, a key containing `SECRET`, `PASSWORD`, `TOKEN` or `PRIVATE_KEY` (but not keys ending in `_CLIENT_KEY`) has a value shorter than 32 characters or containing `change`, `replace`, `example` or `xxx` (any case) |
| `SHARED_SECRET` | the same secret-like key has the **same non-empty value** in `staging` and `production` (report once, on `production`) |

**Messages must never contain the values** of secret-like keys (a test checks this).

## 3. `main(paths) -> int`
`python env_parity.py staging=.env.staging production=.env.production --require DATABASE_URL,JWT_SECRET_KEY` prints `production JWT_SECRET_KEY WEAK_SECRET: <message>` per issue and returns `1` if there are issues, else `0`.

```bash
cd exercises
uv run pytest m5/w2/03-env-parity
```

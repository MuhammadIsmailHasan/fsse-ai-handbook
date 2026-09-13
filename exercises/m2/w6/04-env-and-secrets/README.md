# M2 · W6 · 04 — Fail-Fast Settings and a Secret Scanner

> 🚫🤖 **No-AI** · ⏱️ ~90 min · no database needed

## Part 1 — `settings.py`
`load_settings(env: Mapping[str, str]) -> Settings` (pass `os.environ` in real code; tests pass plain dicts).

| Variable | Rule |
|---|---|
| `APP_ENV` | `development` (default), `test` or `production` |
| `DATABASE_URL` | required in every environment (blank counts as missing) |
| `JWT_SECRET_KEY` | **production:** required, ≥ 32 chars, not a known placeholder (`secret`, `changeme`, `change-me`, `dev`, `password`, `super-secret-key-change-in-production`, case-insensitive). **Other envs:** if missing, use a default that contains the word `insecure` and is ≥ 32 chars |
| `DEBUG` | `true/1/yes/on` or `false/0/no/off` (case-insensitive), default false; **must be false in production** |
| `PORT` | integer 1–65535, default `5091` |
| `CORS_ORIGINS` | comma-separated → tuple of stripped values (empty → `()`); `*` not allowed in production |

- Collect **all** problems, then raise `SettingsError(errors)` once. Each error message **starts with the variable name** (e.g. `"PORT must be…"`) and **never includes the value**.
- `repr(settings)` must not show the database URL or the JWT secret (hint: `field(repr=False)`).
- `settings.safe_summary()` → a dict safe to log: secret as `"***"`, the password inside `DATABASE_URL` as `***`, `cors_origins` as a list.

## Part 2 — `scan_secrets.py`
`scan_text(text, path) -> list[Finding(path, line, kind)]` — one finding per matching line, in line order:
| kind | Detects |
|---|---|
| `aws_access_key` | `AKIA` + 16 uppercase letters/digits |
| `github_token` | `ghp_` + 36 letters/digits, or `github_pat_` + 22+ letters/digits/underscores |
| `private_key` | `-----BEGIN PRIVATE KEY-----` (also `RSA `, `EC `, `OPENSSH ` variants) |
| `hardcoded_secret` | only if no kind above matched: a name containing `secret`, `password`, `passwd`, `token`, `api_key` or `apikey` (case-insensitive, name may be quoted) assigned with `=` or `:` to a value of **≥ 8 characters** |

Not a `hardcoded_secret`: lines that read config (`os.environ`, `getenv`, `environ.get`, `config[`, `settings.`), placeholders (`change-me`, `changeme`, `your-…`, `xxx…`, `***`, `<…>`, `${…}`, `$VAR`, `none`, `null`, `test`, `example…`, `dummy…`), and function calls like `hash_password(password)`.

`scan_directory(root)` → findings for every file under `root`, sorted by path (relative, `/`-separated). Skip `.git`, `node_modules`, `.venv`, `__pycache__` and binary files. A file named `.env` or `.env.<anything>` (except `*.example`) is reported as `Finding(path, 0, "env_file")` without scanning its contents.

```bash
cd exercises
uv run pytest m2/w6/04-env-and-secrets

# try it on a real project (replace the path):
uv run python -c "import sys; sys.path.insert(0, 'm2/w6/04-env-and-secrets'); from scan_secrets import scan_directory; print(*scan_directory('/path/to/your/revoshop'), sep='\n')"
```

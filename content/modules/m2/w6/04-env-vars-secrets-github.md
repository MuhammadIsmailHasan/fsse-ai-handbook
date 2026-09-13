---
title: "Security: Environment Variables & GitHub"
summary: Keep configuration out of code and secrets out of Git — typed fail-fast settings, .env files done right, secret scanning, GitHub account and repository security, and what to do when a secret leaks.
type: lesson
source: core
sourceRef: "M2 · W6 · L4"
roles: { be: core, fe: core, fs: core, ai: core, ops: core }
durationMinutes: 150
tags: [security, configuration, secrets, environment-variables, github, twelve-factor]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- **Config vs code** (the Twelve-Factor idea) and why environment variables
- `.env` / `.env.example` / `.gitignore` — the right way
- **Typed, validated, fail-fast** settings instead of silent defaults
- Where secrets live in **CI** and **production** (GitHub Actions secrets, secret managers)
- **Secret scanning** (gitleaks, GitHub push protection) and pre-commit hooks
- GitHub security basics: 2FA, SSH keys, fine-grained tokens, branch protection, Dependabot
- The **leaked secret playbook**: rotate first, then clean up

## 🧠 The big idea

Your code is the **house plan** — you can show it to anyone. Secrets are the **house keys**. You don't glue the keys to the plan, and you definitely don't photocopy the plan (git clone) with the keys attached.

Environment variables are the **key hook by the door** of each house: the same plan works in every house (dev laptop, CI, production), and each house has its own keys.

## ❓ Why does this exist?

- The same code runs in development, test, staging and production with **different** databases, keys and settings.
- Secrets in Git are **forever**: every clone, fork, CI cache and backup keeps them, even after you delete the line.
- Bots scan public GitHub continuously; leaked cloud keys are abused within **minutes** (crypto-mining bills, data theft).
- AI keys (OpenAI, Anthropic, etc.) are billed per use — a leaked key can cost real money fast.

## 💥 What happens if we DON'T?

```python
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-in-production")
```

Someone forgets to set the variable in production. The app **starts happily** with a secret that's public on GitHub. Anyone can now sign a JWT with `"role": "admin"` — and no alarm goes off.

Other classics:
- `.env` committed in the first commit, "removed" in the second (still in history).
- `DEBUG=True` in production → the Werkzeug debugger lets visitors run Python on your server.
- A `print(config)` in startup logs dumps the database password into your log system.

## 📖 How it works, step by step

### 1. Config belongs in the environment

| Belongs in **code** | Belongs in **environment** |
|---|---|
| API routes, business rules | `DATABASE_URL`, `REDIS_URL` |
| Default page size, validation limits | `JWT_SECRET_KEY`, `OPENAI_API_KEY` |
| Feature logic | `APP_ENV`, `LOG_LEVEL`, `PORT` |
| | Allowed CORS origins, external service URLs |

Rule of thumb from [The Twelve-Factor App](https://12factor.net/config): could you open-source the repo **right now** without leaking anything? If not, config is in the code.

### 2. `.env` files — local convenience only

```bash
# .env.example  ← COMMITTED: documents every variable, with placeholders
APP_ENV=development
DATABASE_URL=postgresql://fsse:fsse@localhost:5491/careerpilot
JWT_SECRET_KEY=change-me
OPENAI_API_KEY=
```

```bash
# .gitignore  ← ignore every real env file, keep the example
.env
.env.*
!.env.example
```

- `cp .env.example .env`, then fill in real values locally.
- `python-dotenv` (or `uv run --env-file .env`) loads it **in development**. In production, the platform (Docker, ECS, Render, GitHub Actions) injects real environment variables — no `.env` file on servers.
- Check: `git check-ignore -v .env` should print the matching `.gitignore` rule.

### 3. Typed, validated, fail-fast settings

Read the environment **once**, at startup, into a typed object — and refuse to start if something's wrong:

```python
@dataclass(frozen=True)
class Settings:
    app_env: str
    database_url: str = field(repr=False)      # never shown in repr / logs
    jwt_secret_key: str = field(repr=False)
    debug: bool
    port: int


def load_settings(env: Mapping[str, str]) -> Settings:
    errors = []
    if env.get("APP_ENV") == "production" and len(env.get("JWT_SECRET_KEY", "")) < 32:
        errors.append("JWT_SECRET_KEY must be at least 32 characters in production")
    ...
    if errors:
        raise SettingsError(errors)      # report ALL problems at once
```

```python
def create_app(settings: Settings | None = None) -> Flask:
    settings = settings or load_settings(os.environ)   # crash at deploy time, not at 2 a.m.
```

- **Fail fast**: a broken deploy that won't start is caught by health checks immediately; a deploy running with a wrong secret is a silent incident.
- Parse types (`"false"` is a truthy string in Python!).
- Taking `env` as a parameter makes it trivially testable — no `monkeypatch` needed.
- Libraries: **pydantic-settings** does this declaratively (you'll use it in the FastAPI module).

:::fastapi
FastAPI projects typically use `pydantic-settings`: `class Settings(BaseSettings): jwt_secret_key: SecretStr = Field(min_length=32)`. `SecretStr` hides the value in `repr` and logs; missing or invalid values raise a validation error at startup.
:::

### 4. Generating a strong secret

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Use a different secret per environment. Never reuse the dev secret in production.

### 5. Secrets in CI and production

```mermaid
flowchart LR
    Dev[".env on your laptop<br/>(git-ignored)"] -.never.-> Git[(GitHub repo)]
    GHS["GitHub Actions secrets<br/>${{ secrets.X }}"] --> CI[CI job env vars]
    SM["Secret manager<br/>AWS Secrets Manager / SSM"] --> Prod[Production containers<br/>env vars at start]
```

- **GitHub Actions**: *Settings → Secrets and variables → Actions*, used as `${{ secrets.OPENAI_API_KEY }}`; masked in logs (lesson 07).
- **Production**: a secret manager (AWS Secrets Manager / SSM Parameter Store — Module 5) or your platform's encrypted env settings. Access is logged and can be rotated.
- Least privilege: the CI key can run tests, not delete production.

### 6. Scanning for secrets

- **gitleaks** / **trufflehog**: scan files and **full git history** for key patterns; run in a pre-commit hook and in CI.
- **GitHub secret scanning & push protection**: blocks pushes containing known token formats. Free on public repositories; on private repositories it's part of the paid GitHub Secret Protection — so for your private repos, run gitleaks yourself.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.1   # pin a release tag (check for the latest)
    hooks:
      - id: gitleaks
```

How scanners work (you'll build a mini one): **known formats** (`AKIA…`, `ghp_…`, private key headers) plus **heuristics** (a variable named `*password*` assigned a long literal), with **allowlists** for placeholders.

### 7. Securing GitHub itself

- [ ] **2FA** on your account (passkey or authenticator app).
- [ ] Push with **SSH keys** (or a credential manager), not passwords in URLs.
- [ ] Use **fine-grained personal access tokens**: one repo, minimum permissions, expiry date.
- [ ] **Branch protection / rulesets** on `main`: require PR + passing CI.
- [ ] **Dependabot alerts & security updates** for vulnerable dependencies; `pip-audit` / `npm audit` locally.
- [ ] Review third-party GitHub Apps and Actions you grant access to; pin actions to versions.

### 8. The leaked-secret playbook

1. **Revoke / rotate the secret immediately** — assume it's already been copied. (Changing Git history does NOT un-leak it.)
2. Check for misuse: provider logs, billing, access logs.
3. Deploy the new secret via env/secret manager.
4. Remove it from the code; if the repo is shared, rewrite history with `git filter-repo` and ask collaborators to re-clone.
5. Add a scanner/pre-commit hook so it doesn't happen again; write a short blameless note.

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| Env vars | universal, simple, twelve-factor | flat strings, visible to the process and its children, no audit trail |
| `.env` file locally | easy onboarding | easy to commit by mistake; must never reach servers |
| Secret manager | audit logs, rotation, fine access control | cost, setup, network dependency at startup |
| Silent defaults | "just works" locally | dangerous in production |
| Fail-fast validation | misconfig caught at deploy | a bit more code; must keep dev defaults convenient |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Anything that differs between environments or is sensitive → environment/secret manager.
- ✅ Validate settings at startup in every service.
- 🚫 Don't put constants that never change per environment into env vars — that's just configuration sprawl.
- 🚫 Don't pass secrets as command-line arguments (visible in `ps`) or in URLs/query strings (logged).

## 🏆 Best practices

- [ ] No secrets in code, commits, issues, screenshots, logs or AI chats.
- [ ] Commit `.env.example` with **every** variable and placeholders; ignore `.env` and `.env.*`.
- [ ] Load settings **once** into a typed object; **fail fast** with all errors listed; no insecure production defaults.
- [ ] Hide secrets in `repr`/logs (`field(repr=False)`, `SecretStr`); log a **safe summary** only.
- [ ] Different, strong (`secrets.token_urlsafe`) secrets per environment; rotate periodically and on staff changes.
- [ ] Run **gitleaks** in a pre-commit hook and in CI; enable push protection where available.
- [ ] Store CI secrets in **GitHub Actions secrets**, production secrets in a **secret manager**.
- [ ] 2FA, SSH keys, fine-grained expiring tokens, branch protection, Dependabot.
- [ ] If a secret leaks: **rotate first**, then investigate and clean history.

## 🏭 How it's used in industry

- Security reviews and SOC 2 / ISO 27001 audits check for secret scanning, rotation and access control.
- Fintech teams in Indonesia (under OJK / Bank Indonesia expectations) keep payment gateway keys in secret managers with strict access logs.
- Platform teams provide `settings` libraries so every service validates config the same way.

## ⚠️ Common mistakes

- `os.getenv("KEY", "some-default-secret")`.
- `bool(os.getenv("DEBUG"))` → `"false"` is `True`.
- `.gitignore` has `.env` but not `.env.docker` / `.env.production`.
- Pasting a `.env` into a chat, issue, or AI assistant to "debug".
- Deleting the leaked line and thinking it's fixed.

:::revoshop
Open RevoShop's `config/base.py`: (1) `JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'super-secret-key-change-in-production')` — exactly the dangerous default from this lesson. What happens if production forgets the variable? (2) `MIDTRANS_SERVER_KEY` defaults to `''`: what error would a user see at checkout, and when would you find out? (3) `.gitignore` ignores `.env` with `!.env.example` — would a file named `.env.docker` be ignored? Test with `git check-ignore -v .env.docker`. (4) Run this lesson's `scan_directory` on your RevoShop folder and triage every finding. (5) Sketch a `load_settings` for RevoShop that fails fast in production.
:::

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

A junior teammate committed `.env` with the Midtrans server key, then pushed a new commit deleting it, and says "it's fine now". Explain why it isn't, and what you'll do in the next 30 minutes.

## 📐 Design it

Design configuration and secrets handling for CareerPilot across **local**, **CI** and **production**: list every variable (DB, JWT, OpenAI/Anthropic key, email provider, CORS, log level), where each value lives in each environment, who can access it, validation rules, and the rotation plan for the AI key.

:::quiz
Show a possible design

| Variable | Local | CI | Production | Validation |
|---|---|---|---|---|
| `APP_ENV` | `.env` = development | workflow env = test | task definition = production | enum |
| `DATABASE_URL` | `.env` (Docker Postgres 5491) | service container URL in workflow | Secrets Manager (RDS credentials) | required |
| `JWT_SECRET_KEY` | optional (insecure dev default) | generated per run in workflow | Secrets Manager, 64 chars | prod ≥ 32, not placeholder |
| `LLM_API_KEY` | your personal key, low spend limit | **not needed** — tests use a fake LLM client | Secrets Manager, project-scoped key with budget alert | required in prod |
| `EMAIL_API_KEY` | empty → console email backend | fake backend | Secrets Manager | required in prod |
| `CORS_ORIGINS` | `http://localhost:3091` | n/a | `https://careerpilot.id` | no `*` in prod |
| `LOG_LEVEL` | DEBUG | INFO | INFO | enum |

**Access:** only the production task role can read production secrets; developers can't read them directly; CI only has test values.
**Rotation (LLM key):** create new key → store as new version in Secrets Manager → rolling deploy → verify → revoke old key; every 90 days and immediately on suspicion. Budget alerts catch abuse.
**Guardrails:** `.env.*` ignored, gitleaks pre-commit + CI job, `safe_summary()` logged at startup.
:::

### 📝 Self-review checklist

- [ ] Every secret has a home per environment — none in Git
- [ ] Tests don't need real third-party keys
- [ ] Production refuses to start with missing/weak secrets
- [ ] A rotation plan exists

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m2/w6/04-env-and-secrets" ai="no-ai" title="Fail-fast settings and a mini secret scanner"}
Part 1: `load_settings(env)` parses and validates environment variables, reports **all** problems at once without leaking values, and hides secrets in `repr` and a safe summary. Part 2: a small scanner that finds AWS keys, GitHub tokens, private keys, hardcoded secret assignments and committed `.env` files — while ignoring placeholders and code that reads config.
:::

:::hints
- Build an `errors` list; append instead of raising; raise once at the end.
- `urllib.parse.urlsplit(url).password` gives you the password to mask.
- Regex building blocks: `\bAKIA[0-9A-Z]{16}\b`, `(?i)` for case-insensitive, named groups `(?P<value>...)`.
- For "not a function call", check what comes right after the value.
- `Path.rglob("*")` + `relative_to(root).parts` to skip folders; catch `UnicodeDecodeError` for binaries.
:::

### 🏆 Stretch goal

Install gitleaks (`brew install gitleaks`) and run `gitleaks git -v` inside your RevoShop repo — it scans the **whole history**. Compare its findings with your scanner.

## ✅ Quick check

:::quiz
Why is `os.getenv("JWT_SECRET_KEY", "dev-secret")` dangerous?

If the variable is missing in production, the app silently runs with a known, public secret — anyone can forge tokens. Production should fail to start instead.
:::

:::quiz
A secret was pushed to GitHub. What's the first step?

Revoke/rotate the secret immediately. Rewriting history comes later and doesn't undo the exposure.
:::

:::quiz
What goes in `.env.example`?

Every variable the app needs, with placeholders or safe local defaults and comments — never real secrets.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Environment variable | Variabel lingkungan (konfigurasi di luar kode) |
| Secret | Rahasia — kunci, token, password |
| Fail fast | Gagal cepat saat startup jika konfigurasi salah |
| Secret manager | Layanan penyimpanan rahasia terenkripsi |
| Rotate a secret | Mengganti rahasia lama dengan yang baru |
| Push protection | Pemblokiran push yang berisi rahasia |
| Least privilege | Hak akses seminimal mungkin |

## 📚 Keep learning

- [The Twelve-Factor App — Config](https://12factor.net/config)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [GitHub Docs — About secret scanning](https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning)
- [gitleaks](https://github.com/gitleaks/gitleaks)

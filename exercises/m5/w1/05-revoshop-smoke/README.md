# M5 · W1 · 05 — RevoShop smoke tests (a tool you'll reuse)

> 🤖✅ Provided tool · used in the 🚀 Ship RevoShop labs (W1 local, W2 CI, W4 AWS)

A **smoke test** answers one question fast: *"Is this deployment basically alive and wired correctly?"* — not "is every feature correct" (that's your unit and API tests).

These checks run against **any** RevoShop URL — local Compose, a staging server, production:

```bash
cd exercises
REVOSHOP_URL=http://localhost:8000 uv run pytest m5/w1/05-revoshop-smoke -v
REVOSHOP_URL=https://api.your-domain.com REVOSHOP_EXPECT_HTTPS=1 uv run pytest m5/w1/05-revoshop-smoke -v
```

Without `REVOSHOP_URL` every test is **skipped** (so the handbook's own test run stays green).

| Check | Why it matters after a deploy |
|---|---|
| health returns 200 with `database: up` | app started **and** can reach PostgreSQL |
| `/docs/swagger-ui` loads | routes registered, static config OK |
| unknown route returns **JSON** 404 | error handlers loaded (not an HTML stack trace) |
| no `Werkzeug` in the `Server` header | the **dev server** isn't serving production traffic |
| register → login → `/users/me` | migrations ran, JWT secret configured, auth works end to end |
| product list has pagination meta | main read path + DB queries work |
| health p95 < 800 ms over 10 calls | no obvious latency/misconfiguration problem |
| (HTTPS only) HSTS header, HTTP→HTTPS redirect | TLS terminated correctly at the proxy |

The register test creates a throwaway **buyer** user named `smoke_<random>` — run it against production only if that's acceptable, or set `REVOSHOP_SKIP_WRITES=1`.

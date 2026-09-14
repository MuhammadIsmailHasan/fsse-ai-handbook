# M4 · W6 · 01 — Playwright setup

> 🚫🤖 **No-AI** · ⏱️ ~60 min

Configure Playwright like a real project and write a first smoke test against the CareerPilot mini app (`../_app/server.mjs`).

In a real Next.js project you'd run `npm init playwright@latest`, which creates a config like this plus an example test and (optionally) a GitHub Actions workflow.

## 1. `playwright.config.ts`
Use `defineConfig` and `devices` from `@playwright/test`.

| Setting | Value |
|---|---|
| `testDir` | `"./e2e"` |
| `fullyParallel` | `true` |
| `forbidOnly` | `true` on CI (`!!process.env.CI`) — a forgotten `test.only` must fail the build |
| `retries` | `2` on CI, `0` locally |
| `workers` | `1` on CI, `undefined` (Playwright decides) locally |
| `reporter` | CI: `[["github"], ["html", { open: "never" }]]` · locally: `[["list"], ["html", { open: "never" }]]` |
| `use.baseURL` | `http://localhost:${PORT}` where `PORT = Number(process.env.PORT ?? 3191)` |
| `use.trace` / `screenshot` | `"on-first-retry"` / `"only-on-failure"` |
| `projects` | `chromium` → `devices["Desktop Chrome"]`; `mobile` → `devices["Pixel 7"]` (both add `channel`, see below) |
| `webServer` | `command: "node ../_app/server.mjs"`, `url: http://localhost:${PORT}/health`, `reuseExistingServer: !process.env.CI`, `timeout: 30_000`, `env: { PORT: String(PORT) }` |

Browser fallback (so you don't have to download browsers if Chrome is installed) — spread `{ channel }` into both projects' `use`:
```ts
import { existsSync } from "node:fs";
import { chromium } from "@playwright/test";
const channel = process.env.PW_CHANNEL ?? (existsSync(chromium.executablePath()) ? undefined : "chrome");
```

## 2. `e2e/smoke.spec.ts`
- visiting `/` while logged out shows the **Log in** heading and the page title is **`Log in · CareerPilot`**
- logging in (`sari@example.com` / `correct-horse`) shows the **Applications** heading and a **Log out** button

Both tests run in both projects (4 runs).

```bash
cd exercises/web
npx playwright test --config m4/w6/01-playwright-setup/playwright.config.ts
npx playwright show-report m4/w6/01-playwright-setup/playwright-report
npx vitest run m4/w6/01-playwright-setup          # the grader
```

---
title: "Playwright Setup"
summary: Start end-to-end testing properly — what E2E tests are for, installing Playwright, a production-ready config (webServer, projects, retries, traces, reporters), locators and web-first assertions, and the debugging tools.
type: lesson
source: core
sourceRef: "M3 · W6 · L1"
roles: { be: optional, fe: core, fs: core, ai: optional, ops: recommended }
durationMinutes: 150
tags: [playwright, e2e, testing, configuration, ci]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Where **end-to-end (E2E)** tests fit next to unit and component tests
- Installing Playwright and what `npm init playwright@latest` generates
- A real `playwright.config.ts`: `webServer`, `baseURL`, `projects`, `retries`, `workers`, `forbidOnly`, traces, reporters
- **Locators** (`getByRole`, `getByLabel`) and **web-first assertions** (`await expect(locator).toBeVisible()`)
- Auto-waiting, and why `waitForTimeout` is a smell
- Debugging: UI mode, `--debug`, trace viewer, codegen

## 🧠 The big idea

Unit tests check the **bricks**; component tests check a **room**; E2E tests walk through the **finished house** like a visitor: open the door (load a page), turn on the lights (click), check the water runs (see the result). They catch problems nobody sees in isolation — a broken redirect, a missing cookie, a form that posts to the wrong URL — but they're slower, so you write **fewer**, for the journeys that matter most.

## ❓ Why does this exist?

Your Next.js app is a chain: browser → proxy → Server Component → Server Action → Flask → Postgres → redirect → re-render. Each piece can be unit-tested and the whole thing can still be broken. Playwright drives **real browsers** (Chromium, Firefox, WebKit) and gives you auto-waiting, isolation (a fresh browser context per test), parallelism and excellent debugging tools.

## 💥 What happens if we DON'T?

- "Works on my machine" releases: login redirects loop in production because of a cookie flag.
- Manual click-through testing before every deploy — skipped when you're in a hurry.
- Or E2E tests written badly: `sleep(3000)`, CSS selectors like `.btn-primary > span`, shared data between tests → flaky suites that everyone ignores.

## 📖 How it works, step by step

### 1. The testing pyramid (or trophy)

| Level | Tool | Speed | Catches |
|---|---|---|---|
| Static | TypeScript, ESLint | instant | typos, wrong types |
| Unit | Vitest | ms | logic in pure functions |
| Component / integration | Vitest + Testing Library | ms–s | UI behavior, state, accessibility |
| **E2E** | **Playwright** | seconds | routing, auth, forms, real browser + server integration |

Many teams follow a "testing trophy": lots of integration/component tests, a thin layer of E2E for **critical journeys** (sign up, log in, the core create flow, checkout).

### 2. Install

```bash
npm init playwright@latest          # asks: TypeScript, tests folder, GitHub Actions workflow, install browsers
# or in an existing project
npm install -D @playwright/test
npx playwright install --with-deps chromium    # browsers (and OS dependencies on Linux/CI)
```

Browsers are downloaded separately from the npm package (to a cache folder). You can also use an installed Google Chrome with `channel: "chrome"`.

### 3. A production-ready config

```ts
// playwright.config.ts
import { defineConfig, devices } from "@playwright/test";

const PORT = Number(process.env.PORT ?? 3091);
const CI = !!process.env.CI;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: CI,                       // a forgotten test.only fails the CI run
  retries: CI ? 2 : 0,                  // retry on CI only — and investigate anything flaky
  workers: CI ? 1 : undefined,          // CI machines are small; locally use your cores
  reporter: CI ? [["github"], ["html", { open: "never" }]] : [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: `http://localhost:${PORT}`,  // page.goto("/login")
    trace: "on-first-retry",              // a full recording when a test is retried
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile", use: { ...devices["Pixel 7"] } },
    // { name: "webkit", use: { ...devices["Desktop Safari"] } },
  ],
  webServer: {
    command: CI ? "npm run build && npm run start" : "npm run dev",
    url: `http://localhost:${PORT}`,
    reuseExistingServer: !CI,             // locally reuse your running dev server
    timeout: 120_000,
  },
});
```

- **`webServer`** starts the app before tests and stops it after.
- **`projects`** run the same tests in several browsers/devices.
- Test against a **production build** in CI (`next build && next start`) — dev mode behaves differently (slower, extra checks).
- Use a non-default port (e.g. 3091) so tests don't collide with other local apps.

### 4. The first test

```ts
// e2e/smoke.spec.ts
import { expect, test } from "@playwright/test";

test("logged-out visitors see the login page", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Log in" })).toBeVisible();
  await expect(page).toHaveTitle("Log in · CareerPilot");
});
```

Each test gets its own `page` in a fresh **browser context** (like an incognito window): no cookies or storage leak between tests.

### 5. Locators — find elements like a user

| Prefer | Example |
|---|---|
| `getByRole` | `page.getByRole("button", { name: "Save application" })` |
| `getByLabel` | `page.getByLabel("Email")` |
| `getByText` | `page.getByText("Application created")` |
| `getByPlaceholder`, `getByAltText`, `getByTitle` | when there's no better option |
| `getByTestId` | stable escape hatch (`data-testid`) for things without accessible names |
| ❌ CSS/XPath | `page.locator(".card > div:nth-child(2) button")` — breaks on refactors |

Role locators double as **accessibility checks**: if you can't find the button by role and name, screen reader users can't either.

Locators are **lazy** and can be chained/filtered: `page.getByRole("row").filter({ hasText: "Data Engineer" }).getByRole("button", { name: "Delete" })`.

### 6. Auto-waiting and web-first assertions

```ts
await page.getByRole("button", { name: "Save" }).click();          // waits until visible, enabled, stable
await expect(page.getByRole("status")).toHaveText("Saved");          // retries until true or timeout (5 s default)
```

```ts
// ❌ checks once, immediately — flaky
expect(await page.getByRole("status").textContent()).toBe("Saved");
// ❌ slow AND still flaky
await page.waitForTimeout(3000);
```

### 7. Debugging toolkit

```bash
npx playwright test --ui                 # UI mode: watch, time-travel through each step
npx playwright test --debug              # step through with the inspector
npx playwright test -g "log in" --project=chromium
npx playwright show-report               # HTML report with traces and screenshots
npx playwright show-trace trace.zip      # trace from CI artifacts
npx playwright codegen localhost:3091    # record actions → generated locators (then clean them up)
```

## ⚖️ Trade-offs

| | ✅ | ❌ |
|---|---|---|
| Playwright | multi-browser, auto-wait, parallel, traces, free | browsers to install; E2E is slower than unit tests |
| Cypress | great interactive runner, big community | runs inside the browser (some multi-tab/origin limits), parallelism via paid cloud |
| Selenium/WebDriver | many languages, legacy grids | more boilerplate, manual waits |
| Manual QA | finds UX issues | not repeatable, slow, skipped under pressure |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Critical user journeys, auth and redirects, cross-page flows, smoke tests after deploy.
- ✅ Regression tests for bugs that only happened with the real browser + server.
- 🚫 Every validation message or edge case of a formatting function — that's unit/component territory.
- 🚫 Testing third-party sites you don't control (mock them with `page.route`).

## 🏆 Best practices

- [ ] Test user-visible behavior with **role/label locators**; add `data-testid` only when needed.
- [ ] Use **web-first assertions**; never `waitForTimeout`.
- [ ] Keep tests **independent** (own data, own context); run `fullyParallel`.
- [ ] `forbidOnly` on CI; retries only on CI, and fix flaky tests instead of hiding them.
- [ ] Traces `on-first-retry`, screenshots on failure, HTML report uploaded as a CI artifact.
- [ ] Run E2E against a **production build** in CI.
- [ ] Configure the port and base URL through environment variables.
- [ ] Keep E2E suites small and fast; tag slow suites and run them nightly if needed.

## 🏭 How it's used in industry

- Playwright (by Microsoft) is widely adopted for web E2E testing and is the default choice in many new Next.js projects; VS Code, Bing and many open-source projects use it.
- Teams run smoke E2E tests on every pull request and a fuller suite before or after production deploys, often against **preview deployments**.
- Playwright traces attached to CI failures replace "can you reproduce it?" conversations.

## ⚠️ Common mistakes

- Forgetting `await` before `expect(locator)...` → the test passes before checking.
- Hard-coding `http://localhost:3000` instead of `baseURL`.
- Running E2E against `next dev` in CI → slow, flaky first compiles.
- Committing `playwright/.auth/*.json`, `test-results/` or `playwright-report/`.
- Using codegen output as-is (brittle selectors, no assertions).

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the "bricks, room, finished house" analogy to a teammate who wants to replace all unit tests with E2E tests "because they test everything".

## 📐 Design it

Plan the **E2E strategy** for CareerPilot's Next.js app: which 5–8 journeys deserve E2E tests, which browsers/devices, how the Flask API and database are provided in CI, and what runs on every pull request vs nightly.

:::quiz
Show a possible plan

**Journeys (PR suite, ~3 min):** log in / log out; protected route redirect with `next`; create application (happy path + one server validation error); move status on the board; delete with confirmation; search + pagination in the URL; mobile navigation menu.

**Projects:** Chromium desktop on every PR; `Pixel 7` for the 2 navigation tests; Firefox + WebKit nightly.

**Backend in CI:** `docker compose` starts Postgres (port 5491) + the Flask API (5091) with a **seeded test database**; `webServer` runs `next build && next start` on 3091; each test creates its own user/data through an API helper (or a seeded user per worker) so tests stay independent; external services (AI, email) mocked with `page.route` or test doubles in the API.

**Nightly:** full cross-browser run, visual snapshots of key pages, Lighthouse CI / Web Vitals budget, E2E against the staging deployment.

**Artifacts:** HTML report + traces uploaded on failure; flaky tests tracked and fixed within a sprint.
:::

### 📝 Self-review checklist

- [ ] E2E covers journeys, not every edge case
- [ ] Tests don't depend on each other's data
- [ ] CI uses a production build

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w6/01-playwright-setup" ai="no-ai" title="Configure Playwright and write smoke tests"}
Write a CI-aware `playwright.config.ts` (webServer, projects for desktop and mobile, retries, reporters, traces) and two smoke tests against the CareerPilot mini app. The grader loads your config with different environment variables and runs your tests in both projects.
:::

:::hints
- `devices["Pixel 7"]` gives a mobile viewport, touch and user agent.
- The mini app runs with `node ../_app/server.mjs`; its health URL is `/health`.
- If Playwright says the browser is missing, either run `npx playwright install chromium` or rely on the `channel: "chrome"` fallback from the README.
:::

## ✅ Quick check

:::quiz
Why is `retries: 2` on CI dangerous if nobody looks at retried tests?

Retries hide flakiness: real race conditions (in the test or in the app) pass on the second try and stay unfixed. Use the HTML report's "flaky" list and traces to fix them.
:::

:::quiz
What's the difference between `page.getByRole("button", { name: "Save" })` and `page.locator("button.save")`?

The role locator matches what users and assistive technology perceive and survives styling refactors; the CSS locator depends on implementation details and doesn't check accessibility.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| End-to-end test | Pengujian ujung ke ujung (seluruh alur aplikasi) |
| Locator | Penunjuk elemen di halaman |
| Assertion | Pernyataan pengecekan hasil |
| Flaky test | Tes yang kadang lulus kadang gagal |
| Trace | Rekaman langkah tes untuk debugging |
| Browser context | Sesi browser terisolasi |

## 📚 Keep learning

- [Playwright docs: Installation](https://playwright.dev/docs/intro) · [Configuration](https://playwright.dev/docs/test-configuration) · [Best Practices](https://playwright.dev/docs/best-practices)
- Next.js docs (bundled): Testing → Playwright
- [Playwright: Trace viewer](https://playwright.dev/docs/trace-viewer)

---
title: "Playwright Setup"
summary: Start end-to-end testing properly — what these tests are for, installing Playwright, a real config (webServer, projects, retries, traces, reporters), locators, assertions that wait, and the debugging tools.
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
- Installing Playwright and what `npm init playwright@latest` creates
- A real `playwright.config.ts`: `webServer`, `baseURL`, `projects`, `retries`, `workers`, `forbidOnly`, traces, reporters
- **Locators** (`getByRole`, `getByLabel`) and **web-first assertions** (`await expect(locator).toBeVisible()`)
- Auto-waiting, and why `waitForTimeout` is a bad sign
- Debugging: UI mode, `--debug`, trace viewer, codegen

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **End-to-end (E2E) test** | A test that uses the whole app in a real browser, like a real user | Tes ujung ke ujung |
| **Playwright** | A tool that controls real browsers from test code | Alat pengendali browser untuk tes |
| **Locator** | A way to find an element on the page ("the Save button") | Penunjuk elemen |
| **Assertion** | A check: "this text should be visible" | Pengecekan hasil |
| **Auto-waiting** | Playwright waits until the element is ready before acting | Menunggu otomatis |
| **Flaky test** | A test that sometimes passes and sometimes fails with no code change | Tes yang tidak stabil |
| **Browser context** | A fresh, separate browser session, like a new incognito window | Sesi browser terpisah |
| **Trace** | A step-by-step recording of a test, for debugging | Rekaman langkah tes |

## 🧠 The big idea

Unit tests check the **bricks**; component tests check a **room**; E2E tests walk through the **finished house** like a visitor: open the door (load a page), turn on the lights (click), check the water runs (see the result).

They catch problems nobody sees in small tests — a broken redirect, a missing cookie, a form that posts to the wrong URL. But they're slow, so you write **only a few**, for the journeys that matter most.

## ❓ Why it matters

Your Next.js app is a chain: browser → proxy → Server Component → Server Action → Flask → Postgres → redirect → re-render. Every piece can pass its own tests while the whole chain is still broken — like every train car being fine but not connected.

Playwright drives **real browsers** (Chromium, Firefox, WebKit) and gives you auto-waiting, a fresh browser per test, parallel runs and great debugging tools.

Without it:

- Releases that "work on my machine": login redirects loop in production because of one cookie setting.
- Clicking through the app by hand before every deploy — and skipping it when you're in a hurry.
- Or badly written E2E tests: `sleep(3000)`, CSS selectors like `.btn-primary > span`, tests sharing data → flaky tests that everyone ignores.

## 📖 Step by step

### 1. The testing pyramid (or trophy)

| Level | Tool | Speed | Catches |
|---|---|---|---|
| Static | TypeScript, ESLint | instant | typos, wrong types |
| Unit | Vitest | ms | logic in pure functions |
| Component / integration | Vitest + Testing Library | ms–s | UI behavior, state, accessibility |
| **E2E** | **Playwright** | seconds | routing, auth, forms, real browser + server working together |

Many teams follow a "testing trophy": lots of component/integration tests, and a thin layer of E2E tests for **critical journeys** (sign up, log in, the main create flow, checkout).

### 2. Install

```bash
npm init playwright@latest          # asks: TypeScript, tests folder, GitHub Actions workflow, install browsers
# or in an existing project
npm install -D @playwright/test
npx playwright install --with-deps chromium    # browsers (and OS dependencies on Linux/CI)
```

Browsers are downloaded separately from the npm package (into a cache folder). You can also use your installed Google Chrome with `channel: "chrome"`.

### 3. A real config

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

- **`webServer`** starts your app before the tests and stops it after.
- **`projects`** run the same tests in several browsers or devices.
- **`forbidOnly`**: a leftover `test.only` would silently skip all other tests — on CI, fail instead.
- In CI, test a **production build** (`next build && next start`). Dev mode is slower and behaves differently — like testing a car in the workshop instead of on the road.
- Use a non-default port (like 3091) so tests don't clash with other local apps.

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

Each test gets its own `page` in a fresh **browser context** (like a new incognito window): no cookies or storage leak from one test to the next.

### 5. Locators — find elements like a user

| Prefer | Example |
|---|---|
| `getByRole` | `page.getByRole("button", { name: "Save application" })` |
| `getByLabel` | `page.getByLabel("Email")` |
| `getByText` | `page.getByText("Application created")` |
| `getByPlaceholder`, `getByAltText`, `getByTitle` | when there's no better option |
| `getByTestId` | a stable backup (`data-testid`) for things without an accessible name |
| ❌ CSS/XPath | `page.locator(".card > div:nth-child(2) button")` — breaks on refactors |

A user doesn't say "click the third div's span"; they say "click **Save**". Find elements the same way. Bonus: role locators are also an **accessibility check** — if you can't find the button by role and name, screen reader users can't either.

Locators only search when used, and can be narrowed step by step: `page.getByRole("row").filter({ hasText: "Data Engineer" }).getByRole("button", { name: "Delete" })`.

### 6. Auto-waiting and assertions that retry

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

A fixed wait is like boiling instant noodles for exactly 3 minutes with your eyes closed — sometimes undercooked, sometimes soggy. `await expect(...)` is tasting the noodles every few seconds and stopping when they're ready.

### 7. Debugging tools

```bash
npx playwright test --ui                 # UI mode: watch, time-travel through each step
npx playwright test --debug              # step through with the inspector
npx playwright test -g "log in" --project=chromium
npx playwright show-report               # HTML report with traces and screenshots
npx playwright show-trace trace.zip      # trace from CI artifacts
npx playwright codegen localhost:3091    # record actions → generated locators (then clean them up)
```

A **trace** is like CCTV footage of the test: every step, the page at that moment, network requests and console logs. When a test fails on CI, you watch the footage instead of guessing.

### When to use E2E tests

- ✅ Critical user journeys, login and redirects, flows across several pages, quick "smoke" checks after deploy.
- ✅ Tests for bugs that only happened with the real browser + server.
- 🚫 Every validation message or edge case of a formatting function — use unit/component tests.
- 🚫 Third-party sites you don't control — fake them with `page.route`.

You may also see **Cypress** (a popular alternative) and **Selenium** (older, more manual waiting) at work.

## ⚠️ Common mistakes

- Forgetting `await` before `expect(locator)...` → the test finishes before checking.
- Hard-coding `http://localhost:3000` instead of using `baseURL`.
- Running E2E against `next dev` in CI → slow, flaky first page loads.
- Committing `playwright/.auth/*.json`, `test-results/` or `playwright-report/`.
- Using codegen output as-is (fragile selectors, no assertions).

## 🏆 Best practices

- [ ] Test what users see, with **role/label locators**; add `data-testid` only when needed.
- [ ] Use **web-first assertions**; never `waitForTimeout`.
- [ ] Keep tests **independent** (own data, own context); run `fullyParallel`.
- [ ] `forbidOnly` on CI; retries only on CI, and fix flaky tests instead of hiding them.
- [ ] Traces `on-first-retry`, screenshots on failure, HTML report uploaded as a CI artifact.
- [ ] Run E2E against a **production build** in CI.
- [ ] Set the port and base URL with environment variables.
- [ ] Keep the E2E suite small and fast; run slow suites nightly if needed.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the "bricks, room, finished house" analogy to a teammate who wants to replace all unit tests with E2E tests "because they test everything".

## 📐 Design it

Plan the **E2E strategy** for CareerPilot's Next.js app: which 5–8 journeys deserve E2E tests, which browsers/devices, how the Flask API and database are started in CI, and what runs on every pull request vs nightly.

:::quiz
Show a possible plan

**Journeys (pull request suite, ~3 min):** log in / log out; protected route redirect with `next`; create application (happy path + one server validation error); move status on the board; delete with confirmation; search + pagination in the URL; mobile navigation menu.

**Projects:** Chromium desktop on every pull request; `Pixel 7` for the 2 navigation tests; Firefox + WebKit nightly.

**Backend in CI:** `docker compose` starts Postgres (port 5491) + the Flask API (5091) with a **seeded test database**; `webServer` runs `next build && next start` on 3091; each test creates its own user/data through an API helper (or one seeded user per worker) so tests stay independent; outside services (AI, email) are faked with `page.route` or test doubles in the API.

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
- `devices["Pixel 7"]` gives a mobile screen size, touch and user agent.
- The mini app runs with `node ../_app/server.mjs`; its health URL is `/health`.
- If Playwright says the browser is missing, either run `npx playwright install chromium` or use the `channel: "chrome"` fallback from the README.
:::

## ✅ Quick check

:::quiz
Why is `retries: 2` on CI dangerous if nobody looks at retried tests?

Retries hide flaky tests: real timing bugs (in the test or in the app) pass on the second try and never get fixed. Use the HTML report's "flaky" list and the traces to fix them.
:::

:::quiz
What's the difference between `page.getByRole("button", { name: "Save" })` and `page.locator("button.save")`?

The role locator matches what users and screen readers see, and survives styling changes. The CSS locator depends on how the HTML happens to be written and doesn't check accessibility.
:::

## 📚 Keep learning

- [Playwright docs: Installation](https://playwright.dev/docs/intro) · [Configuration](https://playwright.dev/docs/test-configuration) · [Best Practices](https://playwright.dev/docs/best-practices)
- Next.js docs (bundled): Testing → Playwright
- [Playwright: Trace viewer](https://playwright.dev/docs/trace-viewer)

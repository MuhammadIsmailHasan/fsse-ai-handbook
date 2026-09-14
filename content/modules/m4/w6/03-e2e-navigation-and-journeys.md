---
title: "E2E: Navigation & User Journeys"
summary: Test how users move through the app — authentication setup projects with storageState, route guards, active links, URL state, back button, 404s, titles and breadcrumbs, full journeys with test.step, and running E2E in CI.
type: lesson
source: core
sourceRef: "M3 · W6 · L3"
roles: { be: optional, fe: core, fs: core, ai: optional, ops: recommended }
durationMinutes: 180
tags: [playwright, e2e, navigation, authentication, storage-state, ci]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Logging in **once** with a setup project and `storageState`
- When a test needs its own session (logout, role changes, data mutations)
- Testing **route guards** and `next` redirects
- Active navigation (`aria-current`), breadcrumbs and page titles
- **URL state**: search params, reloads, back/forward
- Asserting HTTP status (real 404s)
- Long user journeys with **`test.step`**
- Multiple roles, and running E2E in GitHub Actions

## 🧠 The big idea

Navigation tests check the **signposts and doors** of a building: can you get in without a badge (guards)? Does the map say "You are here" (active link)? If you share a room number (URL) with a friend, do they land in the same place (URL state)? Does the "back" door lead where you came from?

A **journey** test is one visitor's whole trip, recorded in chapters (`test.step`), so when something breaks you know which chapter failed.

## ❓ Why does this exist?

Next.js apps have lots of navigation logic: `proxy.ts` redirects, layouts, `Link` prefetching, `useRouter().push/replace`, search params, `notFound()`, metadata titles. Regressions here are common after refactors ("we moved the filters to client state and now links to filtered lists don't work").

## 💥 What happens if we DON'T?

- Search results live only in React state: sharing the URL or pressing refresh loses them.
- A redirect loop between `/login` and `/dashboard` when the cookie is expired.
- `/applications/9999` returns **200** with an empty page — search engines index junk and monitoring never sees errors.
- Every E2E test logs in through the UI: a 40-test suite spends 2 minutes typing passwords.

## 📖 How it works, step by step

### 1. Authenticate once: setup project + `storageState`

```ts
// playwright.config.ts
projects: [
  { name: "setup", testMatch: /.*\.setup\.ts/ },
  { name: "chromium", use: { ...devices["Desktop Chrome"], storageState: "playwright/.auth/user.json" }, dependencies: ["setup"] },
],
```

```ts
// e2e/auth.setup.ts
import { expect, test as setup } from "@playwright/test";

setup("authenticate", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill(process.env.E2E_USER_EMAIL!);
  await page.getByLabel("Password").fill(process.env.E2E_USER_PASSWORD!);
  await page.getByRole("button", { name: "Log in" }).click();
  await expect(page.getByRole("heading", { name: "Applications" })).toBeVisible();   // wait until the cookie is set
  await page.context().storageState({ path: "playwright/.auth/user.json" });
});
```

`storageState` saves cookies and localStorage. Every test in `chromium` starts logged in. Add `playwright/.auth` to `.gitignore` — it's a live session.

For **several roles**, save several files (`member.json`, `admin.json`) and use `test.use({ storageState: "playwright/.auth/admin.json" })` in admin tests.

### 2. Opting out: fresh sessions

```ts
test.describe("without a session", () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  test("protected pages redirect to login", async ({ page }) => {
    await page.goto("/applications");
    await expect(page).toHaveURL(/\/login\?next=%2Fapplications/);
  });
});
```

Logging out **invalidates the shared session on the server**. A logout test must log in by itself, or other tests running in parallel suddenly get redirected to login — a classic "flaky only on CI" bug.

### 3. Active links, breadcrumbs, titles

```ts
const nav = page.getByRole("navigation", { name: "Main" });
await expect(nav.getByRole("link", { name: "Jobs" })).toHaveAttribute("aria-current", "page");

await expect(page).toHaveTitle("Data Engineer · CareerPilot");       // generateMetadata works

await page.getByRole("navigation", { name: "Breadcrumb" }).getByRole("link", { name: "Applications" }).click();
await expect(page).toHaveURL(/\/applications$/);
```

Scoping locators to a landmark (`navigation` with a name) avoids matching the same link text elsewhere.

### 4. URL state, reload and history

```ts
await page.getByLabel("Search jobs").fill("data");
await page.getByRole("button", { name: "Search" }).click();
await expect(page).toHaveURL(/[?&]q=data/);
await page.reload();
await expect(page.getByTestId("result-count")).toHaveText("5 jobs found");

await page.getByRole("link", { name: "Next page" }).click();
await expect(page).toHaveURL(/page=2/);
await page.goBack();
await expect(page.getByRole("navigation", { name: "Pagination" })).toContainText("Page 1 of 3");
```

In Next.js, filters that should survive reloads and be shareable belong in `searchParams` (`router.push` for history entries users can go back to, `router.replace` for typing-as-you-search).

### 5. Real status codes

```ts
const response = await page.goto("/applications/9999");
expect(response?.status()).toBe(404);
await expect(page.getByRole("heading", { name: "Application not found" })).toBeVisible();
```

`notFound()` in Next.js returns a 404 for the initial request. Client-side navigations don't produce a new HTTP response, so check status with `page.goto`.

### 6. Journeys with `test.step`

```ts
test("job seeker moves an application forward", async ({ page }) => {
  await test.step("open the application", async () => {
    await page.getByRole("navigation", { name: "Main" }).getByRole("link", { name: "Applications" }).click();
    await page.getByRole("link", { name: "Backend Engineer" }).click();
  });
  await test.step("move it to interview", async () => {
    await page.getByLabel("Move to").selectOption("interview");
    await page.getByRole("button", { name: "Update status" }).click();
    await expect(page.getByRole("status")).toHaveText("Status updated");
  });
  await test.step("see it in the list", async () => {
    await page.getByRole("navigation", { name: "Breadcrumb" }).getByRole("link", { name: "Applications" }).click();
    await expect(page.getByRole("row", { name: /Backend Engineer/ })).toContainText("interview");
  });
});
```

Steps show up in the HTML report and traces, so a failure reads "failed at: move it to interview".

### 7. E2E in GitHub Actions

```yaml
e2e:
  needs: quality
  runs-on: ubuntu-latest
  timeout-minutes: 20
  services:
    postgres:
      image: postgres:18-alpine
      env: { POSTGRES_PASSWORD: postgres }
      ports: ["5491:5432"]
  steps:
    - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
    - uses: actions/setup-node@820762786026740c76f36085b0efc47a31fe5020 # v7.0.0
      with: { node-version: 24, cache: npm }
    - run: npm ci
    - run: npx playwright install --with-deps chromium
    - run: npm run build
    - run: npx playwright test
      env:
        E2E_USER_EMAIL: ${{ secrets.E2E_USER_EMAIL }}
        E2E_USER_PASSWORD: ${{ secrets.E2E_USER_PASSWORD }}
    - uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1
      if: failure()
      with: { name: playwright-report, path: playwright-report, retention-days: 7 }
```

For bigger suites, **shard** across machines: `npx playwright test --shard=1/4` in a matrix, then merge reports.

## ⚖️ Trade-offs

| | ✅ | ❌ |
|---|---|---|
| Shared `storageState` | very fast | shared server-side session and data; logout/role tests need care |
| Login per test (UI) | fully isolated | slow |
| Login per test via API (`request.post` + set cookies) | isolated and fast | needs an API login path; skips the login UI (test it separately once) |
| Long journeys | realistic, catch integration bugs | slower, failures less specific (use `test.step`) |
| Many small navigation tests | precise failures | may miss cross-page state bugs |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Guards, redirects with `next`, 404s, URL state, the top 1–3 journeys.
- ✅ Separate storage states per role for RBAC-visible navigation.
- 🚫 Don't test every link on every page — a link-checker or component tests cover that cheaper.
- 🚫 Don't reuse a session for tests that change the session itself.

## 🏆 Best practices

- [ ] Log in once per role with a setup project; keep `.auth` files out of Git.
- [ ] Use `storageState: { cookies: [], origins: [] }` for anonymous tests.
- [ ] Give logout/password-change tests their own session.
- [ ] Scope locators to landmarks (`navigation` with a name, `main`, `dialog`).
- [ ] Assert `aria-current`, titles and breadcrumbs — they're user-facing.
- [ ] Put shareable state in the URL and test reload + back.
- [ ] Check real HTTP status for error pages.
- [ ] Structure journeys with `test.step`; keep them few.
- [ ] Store E2E credentials in CI secrets; use a dedicated test account, never a real user.

## 🏭 How it's used in industry

- The setup-project + `storageState` pattern is Playwright's recommended authentication approach and is used widely to keep suites fast.
- Teams run E2E journeys against preview deployments (Vercel/Netlify previews, ephemeral Kubernetes namespaces) on every pull request.
- Synthetic monitoring tools (Checkly, Datadog Synthetics, Grafana) run Playwright journeys against production every few minutes to detect outages.

## ⚠️ Common mistakes

- Committing `playwright/.auth/user.json` (it's a working session!).
- A logout test sharing the saved session → random failures in other tests.
- Checking status code after a client-side navigation (there's no new response).
- Selecting the "Applications" link and accidentally matching the breadcrumb and nav — ambiguity errors in strict mode.
- `toHaveURL("/jobs?q=data")` with exact strings when parameter order may change — use regex or `URL` parsing.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain why a logout test that reuses the shared `storageState` can make *other* tests fail randomly, and only sometimes.

## 📐 Design it

CareerPilot has three roles (member, mentor, admin). Design the Playwright project setup (setup files, storage states, which projects depend on which) and list the navigation tests for RBAC: what each role should and shouldn't see and reach.

:::quiz
Show a possible design

```ts
projects: [
  { name: "setup", testMatch: /auth\.setup\.ts/ },          // logs in 3 test accounts, saves member.json / mentor.json / admin.json
  { name: "member", testMatch: /member\/.*\.spec\.ts/, use: { storageState: ".auth/member.json" }, dependencies: ["setup"] },
  { name: "mentor", testMatch: /mentor\/.*\.spec\.ts/, use: { storageState: ".auth/mentor.json" }, dependencies: ["setup"] },
  { name: "admin",  testMatch: /admin\/.*\.spec\.ts/,  use: { storageState: ".auth/admin.json" },  dependencies: ["setup"] },
  { name: "anonymous", testMatch: /anonymous\/.*\.spec\.ts/, use: { storageState: { cookies: [], origins: [] } } },
]
```

| Role | Sees in nav | Direct URL checks |
|---|---|---|
| anonymous | — | `/applications`, `/admin/companies` → login with `next` |
| member | Dashboard, My applications | `/mentees` and `/admin/companies` → 404 (or 403 page); another user's `/applications/:id` → 404 |
| mentor | + Mentees | mentee's application visible read-only (no Edit button); non-mentee's → 404; `/admin/*` → 404 |
| admin | + Companies, Users | can open all; "Delete company" visible |

Plus: an API-level check (Playwright `request` fixture) that a member calling the admin Server Action/route gets 403 — UI hiding isn't enough.
:::

### 📝 Self-review checklist

- [ ] One storage state per role
- [ ] Direct-URL access tested, not only hidden links
- [ ] Anonymous project has no session

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w6/03-e2e-navigation-journeys" ai="no-ai" title="Navigation tests with a saved session"}
Write an authentication setup that saves `storageState`, navigation tests (guard, active link, URL search, pagination and back, 404, title and breadcrumb) and journeys (logout with its own session, a multi-step journey). Graded by 8 mutants.
:::

:::hints
- `page.goto()` returns the response — use it for the 404 status.
- Scope nav links: `page.getByRole("navigation", { name: "Main" })`.
- Think about which tests change server-side session state.
:::

## ✅ Quick check

:::quiz
A test asserts `await expect(page).toHaveURL("/login")` after visiting `/applications` logged out, but the app redirects to `/login?next=%2Fapplications`. What happens and how do you write it better?

It fails (exact match including the query). Use a regular expression, e.g. `/\/login\?next=%2Fapplications/`, which also verifies the `next` parameter.
:::

:::quiz
Why use `test.step` in long journeys?

Reports and traces show which step failed, making long tests debuggable without splitting them into many dependent tests.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Route guard | Penjaga rute (cek akses halaman) |
| Storage state | Status penyimpanan browser (cookie, localStorage) |
| Breadcrumb | Jejak navigasi |
| User journey | Perjalanan pengguna melalui fitur |
| Sharding | Membagi tes ke beberapa mesin |
| Synthetic monitoring | Pemantauan dengan tes otomatis terjadwal |

## 📚 Keep learning

- [Playwright: Authentication](https://playwright.dev/docs/auth) · [Projects & dependencies](https://playwright.dev/docs/test-projects) · [Sharding](https://playwright.dev/docs/test-sharding)
- [Playwright: Continuous Integration](https://playwright.dev/docs/ci)

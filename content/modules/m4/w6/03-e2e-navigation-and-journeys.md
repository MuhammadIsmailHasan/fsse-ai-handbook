---
title: "E2E: Navigation & User Journeys"
summary: Test how users move through the app — logging in once with storageState, protected pages, active links, URL state, the back button, 404s, titles and breadcrumbs, full journeys with test.step, and running E2E in CI.
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
- When a test needs its own session (logout, role changes)
- Testing **route guards** and `next` redirects
- Active navigation (`aria-current`), breadcrumbs and page titles
- **URL state**: search params, reloads, back/forward
- Checking the real HTTP status (true 404s)
- Long user journeys with **`test.step`**
- Several roles, and running E2E in GitHub Actions

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Session** | The server remembering you're logged in (usually through a cookie) | Sesi login |
| **`storageState`** | A file with the browser's saved cookies and localStorage | Simpanan status browser |
| **Setup project** | A Playwright project that runs first to prepare things (like logging in) | Proyek persiapan |
| **Route guard** | A check that sends you away from a page you're not allowed to see | Penjaga halaman |
| **URL state** | Page state kept in the address, like `?q=data&page=2` | State di URL |
| **Breadcrumb** | The "Home › Applications › Data Engineer" trail | Jejak navigasi |
| **User journey** | A user's full trip through several pages to finish a task | Perjalanan pengguna |
| **Sharding** | Splitting tests across several machines to finish faster | Membagi tes |

## 🧠 The big idea

Navigation tests check the **signs and doors** of a building: can you get in without a badge (guards)? Does the map say "You are here" (active link)? If you share a room number (URL) with a friend, do they arrive at the same place (URL state)? Does the "back" door lead to where you came from?

A **journey** test is one visitor's whole trip, written in chapters (`test.step`), so when something breaks you know which chapter failed.

## ❓ Why it matters

Next.js apps have lots of navigation logic: `proxy.ts` redirects, layouts, `Link`, `useRouter().push/replace`, search params, `notFound()`, page titles. It often breaks after refactors ("we moved the filters into React state and now shared links to filtered lists don't work").

Without these tests:

- Search results live only in React state: sharing the URL or pressing refresh loses them.
- A redirect loop between `/login` and `/dashboard` when the cookie has expired.
- `/applications/9999` returns **200** with an empty page — search engines save junk and monitoring never sees an error.
- Every test logs in through the UI: a 40-test suite spends 2 minutes typing passwords.

## 📖 Step by step

### 1. Log in once: setup project + `storageState`

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

Like a hotel: you check in at the front desk **once** and get a key card. After that you just tap the card, instead of queuing at reception every time.

- `storageState` saves the cookies and localStorage. Every test in `chromium` starts already logged in.
- Add `playwright/.auth` to `.gitignore` — it's a working key card.
- For **several roles**, save several files (`member.json`, `admin.json`) and use `test.use({ storageState: "playwright/.auth/admin.json" })` in admin tests.

### 2. Tests that need a fresh session

```ts
test.describe("without a session", () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  test("protected pages redirect to login", async ({ page }) => {
    await page.goto("/applications");
    await expect(page).toHaveURL(/\/login\?next=%2Fapplications/);
  });
});
```

Logging out **cancels the shared session on the server** — like reporting the shared key card as lost: every guest using a copy is suddenly locked out. So a logout test must log in by itself. Otherwise other tests running at the same time get sent to the login page — a classic "only fails on CI" bug.

### 3. Active links, breadcrumbs, titles

```ts
const nav = page.getByRole("navigation", { name: "Main" });
await expect(nav.getByRole("link", { name: "Jobs" })).toHaveAttribute("aria-current", "page");

await expect(page).toHaveTitle("Data Engineer · CareerPilot");       // generateMetadata works

await page.getByRole("navigation", { name: "Breadcrumb" }).getByRole("link", { name: "Applications" }).click();
await expect(page).toHaveURL(/\/applications$/);
```

The same link text can appear in the main menu **and** the breadcrumb. Searching inside a named area (`navigation` with a name) picks the right one — like saying "the Applications sign **on the 2nd floor**".

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

In Next.js, filters that should survive a reload and be shareable belong in `searchParams`. Use `router.push` when users should be able to go back to the step, and `router.replace` for search-as-you-type (so Back doesn't walk through every letter).

### 5. Real status codes

```ts
const response = await page.goto("/applications/9999");
expect(response?.status()).toBe(404);
await expect(page.getByRole("heading", { name: "Application not found" })).toBeVisible();
```

`notFound()` in Next.js returns a 404 for the first request. Clicking a link inside the app doesn't create a new HTTP response, so check the status with `page.goto`.

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

Steps appear in the HTML report and traces, so a failure says "failed at: move it to interview" — like a package tracker showing which stop it got stuck at.

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

- The test account's email and password come from **CI secrets**, never from the code.
- The report is uploaded only when tests fail, so you can open the traces.
- For bigger suites, **shard** across machines: `npx playwright test --shard=1/4` in a matrix, then merge the reports.

### Choosing how to log in

| | ✅ | ❌ |
|---|---|---|
| Shared `storageState` | very fast | shared session and data; logout/role tests need care |
| Log in per test through the UI | fully separate | slow |
| Log in per test through the API | separate and fast | needs an API login; skips the login UI (test that once on its own) |

- ✅ Test guards, `next` redirects, 404s, URL state, and the top 1–3 journeys.
- 🚫 Don't test every link on every page — a link checker or component tests do that cheaper.

## ⚠️ Common mistakes

- Committing `playwright/.auth/user.json` (it's a working session!).
- A logout test using the shared session → random failures in other tests.
- Checking the status code after clicking a link inside the app (there's no new response).
- Selecting "Applications" and matching both the breadcrumb and the menu → Playwright's strict mode error.
- `toHaveURL("/jobs?q=data")` as an exact string when parameter order may change — use a regex or parse the `URL`.

## 🏆 Best practices

- [ ] Log in once per role with a setup project; keep `.auth` files out of Git.
- [ ] Use `storageState: { cookies: [], origins: [] }` for logged-out tests.
- [ ] Give logout and password-change tests their own session.
- [ ] Search inside named areas (`navigation` with a name, `main`, `dialog`).
- [ ] Check `aria-current`, titles and breadcrumbs — users see them.
- [ ] Put shareable state in the URL and test reload + back.
- [ ] Check the real HTTP status for error pages.
- [ ] Split journeys with `test.step`; keep only a few.
- [ ] Keep E2E credentials in CI secrets; use a dedicated test account, never a real user.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain, with the hotel key card analogy, why a logout test that reuses the shared `storageState` can make *other* tests fail randomly, and only sometimes.

## 📐 Design it

CareerPilot has three roles (member, mentor, admin). Design the Playwright project setup (setup files, storage states, which projects depend on which) and list the navigation tests for permissions: what each role should and shouldn't see and reach.

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
| mentor | + Mentees | a mentee's application visible read-only (no Edit button); a non-mentee's → 404; `/admin/*` → 404 |
| admin | + Companies, Users | can open all; "Delete company" visible |

Plus: an API-level check (Playwright's `request` fixture) that a member calling the admin Server Action/route gets 403 — hiding it in the UI isn't enough.
:::

### 📝 Self-review checklist

- [ ] One storage state per role
- [ ] Typing the URL directly is tested, not only hidden links
- [ ] The anonymous project has no session

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w6/03-e2e-navigation-journeys" ai="no-ai" title="Navigation tests with a saved session"}
Write an authentication setup that saves `storageState`, navigation tests (guard, active link, URL search, pagination and back, 404, title and breadcrumb) and journeys (logout with its own session, a multi-step journey). Graded by 8 mutants.
:::

:::hints
- `page.goto()` returns the response — use it for the 404 status.
- Search inside the menu: `page.getByRole("navigation", { name: "Main" })`.
- Think about which tests change the session on the server.
:::

## ✅ Quick check

:::quiz
A test checks `await expect(page).toHaveURL("/login")` after visiting `/applications` logged out, but the app redirects to `/login?next=%2Fapplications`. What happens, and how do you write it better?

It fails (an exact string must include the query). Use a regular expression, e.g. `/\/login\?next=%2Fapplications/`, which also checks the `next` parameter.
:::

:::quiz
Why use `test.step` in long journeys?

Reports and traces show which step failed, so long tests stay easy to debug without splitting them into many tests that depend on each other.
:::

## 📚 Keep learning

- [Playwright: Authentication](https://playwright.dev/docs/auth) · [Projects & dependencies](https://playwright.dev/docs/test-projects) · [Sharding](https://playwright.dev/docs/test-sharding)
- [Playwright: Continuous Integration](https://playwright.dev/docs/ci)

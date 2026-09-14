# M4 · W6 · 03 — E2E: navigation and user journeys

> 🚫🤖 **No-AI** · ⏱️ ~2 h · 🧪 **graded by 8 mutants**

Same mini app as exercise 02. This time: **log in once**, reuse the session, and test navigation — guards, links, URLs, titles, 404s — plus one full user journey.

## 1. `e2e/auth.setup.ts`
The provided config runs files matching `*.setup.ts` in a `setup` project first. Write a `setup("authenticate", …)` (import `test as setup`) that logs in as `sari@example.com` / `correct-horse`, waits for the **Applications** heading and saves `page.context().storageState({ path: "playwright/.auth/user.json" })`.

All tests in the `chromium` project then start **already logged in**.

## 2. `e2e/navigation.spec.ts`
- **Guard:** a visitor with **no session** (`test.use({ storageState: { cookies: [], origins: [] } })` in a `describe`) who opens `/applications` lands on `/login?next=…`
- **Active link:** on `/jobs`, the **Jobs** link in the *Main* navigation has `aria-current="page"` and **Applications** doesn't
- **Search is in the URL:** searching `data` updates the URL to `?q=data`, shows **"5 jobs found"** (search is case-insensitive: *Data Engineer*, *Big Data Engineer*, …), and **reloading** keeps the results
- **Pagination:** `/jobs` shows "Page 1 of 3"; **Next page** → "Page 2 of 3" and the URL has `page=2`; the browser **back** button returns to page 1
- **404:** `/applications/9999` responds with HTTP **404** and the heading **"Application not found"** (`const response = await page.goto(...)`)
- **Titles and breadcrumbs:** an application's page title is **`{role} · CareerPilot`** and its **Applications** breadcrumb link goes back to `/applications`

## 3. `e2e/journeys.spec.ts`
- **Log out:** log in **fresh** in this test (don't log out the shared session — why?), click **Log out**, then opening `/applications` must send you to the login page
- **A job seeker's journey** (one longer test using `test.step`): dashboard → Applications → open *Backend Engineer* → move to `interview` → back to the list via breadcrumb → the row shows `interview`

```bash
cd exercises/web
npx playwright test --config m4/w6/03-e2e-navigation-journeys/playwright.config.ts
npx vitest run m4/w6/03-e2e-navigation-journeys
```

:::tip
The shared session is shared **data** too. Tests that change data should use data nobody else asserts on — or their own login.
:::

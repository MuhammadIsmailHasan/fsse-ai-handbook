# M4 · W6 · 02 — E2E: forms and flows with Playwright

> 🚫🤖 **No-AI** · ⏱️ ~2 h · 🧪 **graded by mutants**

You write the **tests** this time. `../_app/server.mjs` is a tiny stand-in for CareerPilot (login, applications, a form, a detail page). The grader runs your tests:

1. against the **correct** app → all your tests must **pass**
2. against **9 broken copies** of the app (each with one bug) → each broken copy must make **at least one** of your tests **fail**

A copy your tests don't catch "survived" — a real bug that would reach users.

> Don't read `server.mjs`'s bug switches. Write tests from the behavior below, like you would from a product spec.

## Setup
```bash
cd exercises/web
npx playwright install chromium        # or skip if Google Chrome is installed — the config falls back to it
npx playwright test --config m4/w6/02-e2e-forms-flows/playwright.config.ts          # run your tests
npx playwright test --config m4/w6/02-e2e-forms-flows/playwright.config.ts --ui     # watch mode with time travel
npx vitest run m4/w6/02-e2e-forms-flows                                             # the grader
```
Login: `sari@example.com` / `correct-horse`. Every login gets **fresh data** (2 applications: *Backend Engineer*, *Data Engineer*), so tests don't affect each other.

## 1. Page objects — `e2e/pages/`
- `login-page.ts`: `LoginPage` with `goto()`, `login(email, password)`, and locators `email`, `password`, `submit`, `alert`
- `new-application-page.ts`: `NewApplicationPage` with `goto()`, `fill({ company?, role?, salaryMin?, salaryMax? })`, `submit()` and locators for each field
Use **role/label locators** (`getByLabel`, `getByRole`) — no CSS classes or XPath.

## 2. Tests — `e2e/application-forms.spec.ts`
Behavior to cover:

**Login**
- a wrong password shows the alert **"Invalid email or password"** and stays on `/login`
- opening `/applications/new` while logged out goes to the login page; after logging in you land **back on `/applications/new`**

**New application form**
- submitting without a role shows **"Role is required"**, marks the field `aria-invalid="true"`, and **keeps what you typed** in other fields
- a maximum salary lower than the minimum shows **"Maximum must be at least the minimum"**
- a valid submission opens the new application's page (heading = role) with the status message **"Application created"**, and the application **appears in the list** at `/applications`

**Application page**
- changing the status with **Move to** + **Update status** is **still there after a reload**
- **Delete** opens a confirmation dialog: **Cancel** keeps the application; **Delete application** removes it, shows **"Application deleted"** and it's gone from the list

## Rules of thumb
- Web-first assertions (`await expect(locator).toHaveText(...)`) — never `waitForTimeout`
- One behavior per test; independent tests (log in inside each test or in a `beforeEach`)
- Assert what the **user** sees (text, roles, URL), not implementation details

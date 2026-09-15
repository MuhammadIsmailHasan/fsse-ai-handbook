---
title: "Week 6 Placement Check"
summary: Playwright setup and end-to-end tests, page objects and saved logins, component tests, smaller builds, deploying Next.js with Docker, and Core Web Vitals — check what you can skip.
type: placement-check
source: original
roles: { be: optional, fe: core, fs: core, ai: recommended, ops: recommended }
durationMinutes: 20
tags: [placement, testing, playwright, deployment, performance]
---

::::placement{id="modules/m4/w6"}
Answer from memory. If a word is new to you, that's a sign to study the lesson.

:::quiz
1 · Your Playwright test does `await page.click("#save"); await page.waitForTimeout(2000); expect(await page.textContent(".toast")).toBe("Saved")`. Name three problems.

A fixed wait (sleep) is slow and can still fail randomly ("flaky"). CSS/ID selectors break when the HTML changes and ignore accessibility. `expect(await …)` checks only once instead of retrying. Better: `await page.getByRole("button", { name: "Save" }).click()` and `await expect(page.getByRole("status")).toHaveText("Saved")`.
:::

:::quiz
2 · How do you avoid logging in through the UI in every end-to-end test, and which test must not reuse that saved login?

A setup project logs in once and saves the cookies to a file (`storageState`); the other tests load that file. A test that logs out (or changes the user's password or security) must use its own fresh login — otherwise it breaks the shared one for everyone.
:::

:::quiz
3 · Unit, component, end-to-end: which would you use to test (a) salary range formatting, (b) a table's filtering and delete button states, (c) "a user logs in and creates an application"?

(a) unit test, (b) component test with Vitest + Testing Library, (c) end-to-end test with Playwright. Most tests should be the fast, cheap kinds; a few end-to-end tests cover the most important journeys.
:::

:::quiz
4 · Name three changes that usually shrink the JavaScript a Next.js page sends on first load.

Move non-interactive work (markdown, code highlighting) into Server Components; load heavy browser-only widgets later with `next/dynamic`; put `"use client"` only on small leaf components; avoid huge libraries or use `optimizePackageImports`.
:::

:::quiz
5 · What does `output: "standalone"` do, and why should the final Docker stage run as a non-root user?

It makes `next build` produce a small `server.js` with only the `node_modules` it really needs, so the image stays small. Running as non-root limits the damage if someone breaks into the app.
:::

:::quiz
6 · What are LCP, INP and CLS, and what are the "good" limits?

Largest Contentful Paint ≤ 2.5 s (how fast the main content shows), Interaction to Next Paint ≤ 200 ms (how fast the page reacts to a click or key), Cumulative Layout Shift ≤ 0.1 (how little things jump around) — measured at the 75th percentile of real visits.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6**. Even if you pass, do the mutant-graded exercises (02, 03, 06) — writing tests that catch real bugs is a skill interviewers check.
:::

---
title: "Week 6 Placement Check"
summary: Playwright configuration and E2E testing, page objects and saved sessions, component tests, build optimization, Docker deployment of Next.js and Core Web Vitals — check what you can skip.
type: placement-check
source: original
roles: { be: optional, fe: core, fs: core, ai: recommended, ops: recommended }
durationMinutes: 20
tags: [placement, testing, playwright, deployment, performance]
---

::::placement{id="modules/m4/w6"}
:::quiz
1 · Your Playwright test does `await page.click("#save"); await page.waitForTimeout(2000); expect(await page.textContent(".toast")).toBe("Saved")`. Name three problems.

Fixed sleeps are slow and still flaky; CSS/ID selectors break on markup changes and ignore accessibility; `expect(await …)` checks once instead of retrying. Use `await page.getByRole("button", { name: "Save" }).click()` and `await expect(page.getByRole("status")).toHaveText("Saved")`.
:::

:::quiz
2 · How do you avoid logging in through the UI in every E2E test, and which test must not reuse that session?

A setup project logs in once and saves `storageState` to a file; other projects load it. Tests that log out (or change the user's security state) must use their own fresh session, or they break the shared one.
:::

:::quiz
3 · Unit, component, E2E: which would you use to test (a) salary range formatting, (b) a table's filtering and delete button states, (c) "a user logs in and creates an application"?

(a) unit test, (b) component test with Vitest + Testing Library, (c) E2E test with Playwright. Most tests should be the fast, cheap kinds; a few E2E tests cover critical journeys.
:::

:::quiz
4 · Name three changes that usually shrink a Next.js page's first-load JavaScript.

Move non-interactive work (markdown, syntax highlighting) into Server Components; lazy-load heavy client-only widgets with `next/dynamic`; push `"use client"` to leaves; avoid huge dependencies or use `optimizePackageImports`.
:::

:::quiz
5 · What does `output: "standalone"` do, and why should the runtime Docker stage run as a non-root user?

It makes `next build` emit a minimal `server.js` with only the needed `node_modules`, so the image stays small. Non-root limits the damage if the app is compromised.
:::

:::quiz
6 · What are LCP, INP and CLS, and what are the "good" thresholds?

Largest Contentful Paint ≤ 2.5 s (loading), Interaction to Next Paint ≤ 200 ms (responsiveness), Cumulative Layout Shift ≤ 0.1 (visual stability) — measured at the 75th percentile of real page loads.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6**. Even if you pass, do the mutant-graded exercises (02, 03, 06) — writing tests that catch real bugs is a skill interviews probe.
:::

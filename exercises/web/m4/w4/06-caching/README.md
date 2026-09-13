# M4 · W4 · 06 — Caching with Cache Components (`use cache`, `cacheLife`, `cacheTag`, `updateTag`)

> 🚫🤖 **No-AI** · ⏱️ ~75 min

Next.js 16's **Cache Components** model: data is fetched fresh by default, and **you** choose what to cache. Public job listings can be cached for hours; a user's own applications must never be shared between users.

| File | Requirements |
|---|---|
| `next.config.ts` | `const nextConfig: NextConfig = { cacheComponents: true }` as the default export |
| `lib/jobs.ts` | `getPublicJobs()`: first statement `"use cache"`, then `cacheLife("hours")` and `cacheTag("jobs")`; fetch `{API_URL}/api/v1/jobs` (no auth header) and return `data`. `getJob(id)`: `"use cache"`, `cacheLife("hours")`, `cacheTag("jobs", "job-{id}")`; fetch `…/api/v1/jobs/{id}` → `data` |
| `lib/applications.ts` | `getMyApplications(token)`: **not cached** (no `"use cache"` in the file); fetch `…/api/v1/applications` with `Authorization: Bearer {token}` → `data` |
| `app/jobs/page.tsx` | default export page (not async) rendering `<h1>Jobs</h1>`, `<JobList />` and — inside `<Suspense fallback={<p role="status">Loading your applications…</p>}>` — `<MyApplicationsSummary />`. `JobList` is an async component that awaits `getPublicJobs()` and renders `<ul>` of titles. `MyApplicationsSummary` is async, reads the `session` cookie with `await cookies()` (from `next/headers`); without a session it renders `<p>Log in to track applications</p>`, otherwise `<p>You have {n} applications</p>` |
| `app/actions.ts` | a `"use server"` file exporting `closeJob(jobId: number)`: read the `session` cookie — missing → return `{ ok: false, message: "Please log in" }` **without** calling the API. Otherwise `POST …/api/v1/jobs/{id}/close` with the bearer token; not ok → `{ ok: false, message: "Couldn't close the job" }`; ok → `updateTag("jobs")`, `updateTag("job-{id}")`, return `{ ok: true }` |

`API_URL` comes from `process.env.API_URL`. The tests mock `next/cache` and `next/headers` and inspect your directives.

```bash
cd exercises/web
npx vitest run m4/w4/06-caching
```

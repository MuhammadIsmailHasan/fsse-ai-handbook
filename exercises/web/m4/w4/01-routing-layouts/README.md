# M4 · W4 · 01 — File-Based Routing and Layouts

> 🚫🤖 **No-AI** · ⏱️ ~75 min

Build the route files of a small Next.js App Router app inside `app/` (the tests import and render them like Next.js would). Provided: `lib/jobs-data.ts` with `getJobs()` and `getJob(id)`. Use **relative imports** here (in a real project you'd use `@/lib/...`).

## 1. `lib/routes.ts` — `routeFromFile(file)`
Map an App Router file path to its URL, or `null` if it isn't a route:

| Input | Output |
|---|---|
| `app/page.tsx` | `/` |
| `app/jobs/page.tsx` | `/jobs` |
| `app/jobs/[id]/page.tsx` | `/jobs/[id]` |
| `app/(auth)/login/page.tsx` | `/login` (route groups don't appear in the URL) |
| `app/api/health/route.ts` | `/api/health` |
| `app/jobs/_components/row.tsx`, `app/layout.tsx`, `app/jobs/loading.tsx` | `null` (private folders and non-route files) |

## 2. Route files
| File | Requirements |
|---|---|
| `app/layout.tsx` | root layout: `<html lang="en"><body>` with a `<header>` containing `<nav aria-label="Main">` links to `/jobs` ("Jobs") and `/dashboard` ("Dashboard") using `next/link`, then `<main>{children}</main>` |
| `app/page.tsx` | `<h1>CareerPilot</h1>` |
| `app/jobs/page.tsx` | **async** Server Component: `await getJobs()`, `<h1>Jobs</h1>` and a list of links `"{title} · {company}"` to `/jobs/{id}` |
| `app/jobs/[id]/page.tsx` | **async**; props `{ params: Promise<{ id: string }> }`; `await params`; call `notFound()` (from `next/navigation`) if the id isn't a positive integer or the job doesn't exist; otherwise `<h1>{title}</h1>` and `<p>{company} · {city}</p>` |
| `app/jobs/[id]/loading.tsx` | `<p role="status">Loading job…</p>` |
| `app/jobs/[id]/not-found.tsx` | `<h1>Job not found</h1>` and a link "Back to jobs" to `/jobs` |
| `app/(auth)/login/page.tsx` | `<h1>Log in</h1>` |
| `app/dashboard/layout.tsx` | nested layout: `<div>` with `<aside aria-label="Dashboard">` (links "Overview" `/dashboard` and "Applications" `/dashboard/applications`) and `<section>{children}</section>` |
| `app/dashboard/page.tsx` | `<h1>Dashboard</h1>` |

Every page, layout, loading and not-found file uses a **default export**.

```bash
cd exercises/web
npx vitest run m4/w4/01-routing-layouts
```

Want to see it for real? Copy `app/` and `lib/` into a `create-next-app` project and run `npm run dev -- --port 3091`.

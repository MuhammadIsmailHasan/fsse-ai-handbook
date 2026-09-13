---
title: "🔥 Data Fetching & Caching in Next.js 16"
summary: Fetch on the server without waterfalls, stream slow parts with Suspense, and cache deliberately with Cache Components — use cache, cacheLife, cacheTag, updateTag and revalidateTag — without leaking personal data.
type: lesson
source: original
roles: { be: recommended, fe: core, fs: core, ai: recommended, ops: recommended }
durationMinutes: 180
tags: [nextjs, caching, suspense, streaming, use-cache, performance]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Fetching in Server Components: sequential vs parallel, avoiding waterfalls
- Streaming with `loading.tsx` and `<Suspense>`
- The **Cache Components** model (`cacheComponents: true`): dynamic by default, cache what you choose
- `"use cache"` at data and UI level, `cacheLife` profiles, cache keys from arguments
- On-demand invalidation: `cacheTag`, `updateTag` (read-your-own-writes), `revalidateTag`, `revalidatePath`
- Runtime APIs (`cookies`, `headers`, `searchParams`) and why personal data must not be shared
- The previous caching model (`fetch` options, `unstable_cache`) — for older projects

## 🧠 The big idea

Caching is a **restaurant's prep station**. Dishes everyone orders (the public job list) can be prepared ahead and served instantly, refreshed every hour. A dish made to one customer's allergies (their applications) must be cooked fresh for that customer — serving it to someone else is a disaster. The skill is labeling each dish correctly, and throwing out prepped dishes when the recipe changes (invalidation).

## ❓ Why does this exist?

Rendering every page from scratch, calling Flask on every request, is slow and expensive at scale. Serving stale or wrong data is worse. Next.js gives you tools to decide **per function or component** what may be reused, for how long, and how to refresh it after a change.

## 💥 What happens if we DON'T get it right?

- Waterfalls: `await getUser()`, then `await getApplications()`, then `await getStats()` — 3× slower than needed.
- A slow AI match endpoint blocks the whole dashboard.
- Cached personal data: user A sees user B's applications (a privacy incident).
- Editing a job doesn't show up because nobody invalidated the cache.

:::note[Which Next.js caching model?]
Next.js 16 introduced **Cache Components**, enabled with `cacheComponents: true` in `next.config.ts`. This lesson teaches that model (the one the Next.js docs lead with). Projects without the flag use the **previous model** (section 8). Check `next.config.ts` before applying advice from tutorials.
:::

## 📖 How it works, step by step

### 1. Parallel, not sequential

```tsx
// ❌ waterfall
const user = await getUser();
const applications = await getApplications();

// ✅ start together, await together
const [user, applications] = await Promise.all([getUser(), getApplications()]);
```

Sequential is correct only when one request needs the result of another.

### 2. Streaming slow parts

```tsx
export default function DashboardPage() {
  return (
    <>
      <h1>Dashboard</h1>                                   {/* sent immediately */}
      <Suspense fallback={<StatsSkeleton />}>
        <Stats />                                          {/* async; streams when ready */}
      </Suspense>
      <Suspense fallback={<MatchSkeleton />}>
        <AiMatchCard />                                    {/* slow AI call doesn't block Stats */}
      </Suspense>
    </>
  );
}
```

`loading.tsx` wraps a whole page in Suspense; `<Suspense>` gives finer control.

### 3. Enable Cache Components

```ts
// next.config.ts
import type { NextConfig } from "next";
const nextConfig: NextConfig = { cacheComponents: true };
export default nextConfig;
```

With it: fetching is **dynamic by default**; Next.js prerenders a static **shell** and streams dynamic parts. Uncached data or runtime APIs outside `<Suspense>` produce a helpful dev/build error telling you to wrap or cache them.

### 4. `"use cache"` + `cacheLife`

```ts
import { cacheLife, cacheTag } from "next/cache";

export async function getPublicJobs() {
  "use cache";
  cacheLife("hours");        // stale 5m, revalidate 1h, expire 1d
  cacheTag("jobs");
  const res = await fetch(`${process.env.API_URL}/api/v1/jobs`);
  return (await res.json()).data;
}

export async function getJob(id: number) {
  "use cache";
  cacheLife("hours");
  cacheTag("jobs", `job-${id}`);   // arguments are part of the cache key automatically
  …
}
```

| Profile | stale | revalidate | expire |
|---|---|---|---|
| `seconds` | 30s | 1s | 60s |
| `minutes` | 5m | 1m | 1h |
| `hours` | 5m | 1h | 1d |
| `days` | 5m | 1d | 1w |
| `max` | 5m | 30d | 1y |

`"use cache"` can also sit at the top of an async **component** or page (UI-level cache), or at the top of a file (all exports cached). Pair every cache with a `cacheLife`.

### 5. Personal data: never shared

```tsx
async function MyApplicationsSummary() {
  const session = (await cookies()).get("session")?.value;   // runtime API → request-time
  if (!session) return <p>Log in to track applications</p>;
  const applications = await getMyApplications(session);     // NOT "use cache"
  return <p>You have {applications.length} applications</p>;
}

// page
<Suspense fallback={<p role="status">Loading your applications…</p>}>
  <MyApplicationsSummary />
</Suspense>
```

Rules of thumb:
- Data identical for everyone → cache with tags.
- Data per user → no shared cache; fetch at request time behind Suspense. (Advanced: `"use cache: private"` or passing the user id as an argument creates per-user entries — understand the implications before using it.)
- Never read `cookies()`/`headers()` **inside** a `"use cache"` function.

### 6. Invalidate after mutations

```ts
"use server";
import { updateTag } from "next/cache";

export async function closeJob(jobId: number) {
  const session = (await cookies()).get("session")?.value;
  if (!session) return { ok: false, message: "Please log in" };
  const res = await fetch(`${process.env.API_URL}/api/v1/jobs/${jobId}/close`, { method: "POST", headers: { Authorization: `Bearer ${session}` } });
  if (!res.ok) return { ok: false, message: "Couldn't close the job" };
  updateTag("jobs");
  updateTag(`job-${jobId}`);
  return { ok: true };
}
```

| API | Where | Behavior |
|---|---|---|
| `updateTag(tag)` | Server Actions | expire immediately → the user sees their own change |
| `revalidateTag(tag, "max")` | Server Actions, Route Handlers (e.g. a webhook from Flask) | stale-while-revalidate: serve old, refresh in background |
| `revalidatePath(path)` | Server Actions, Route Handlers | invalidate a route when you don't know its tags |

When **Flask** changes data (another user, admin tool), call a Next.js Route Handler webhook that runs `revalidateTag` — the same signed-webhook pattern from Module 2 Week 5.

### 7. Client-side cache

`router.refresh()` re-renders server data for the current route; TanStack Query caches data in the browser for client-fetched data (lesson 07). They're separate layers — know which one holds your stale data.

### 8. The previous model (without `cacheComponents`)

- `fetch` is **not cached** by default (since Next.js 15); opt in with `fetch(url, { cache: "force-cache", next: { revalidate: 3600, tags: ["jobs"] } })`.
- `unstable_cache(fn, keyParts, { tags, revalidate })` for non-fetch data.
- Route segment config: `export const dynamic = "force-dynamic" | "force-static"`, `export const revalidate = 3600`.

You'll meet this in existing codebases and tutorials written for Next.js 13–15.

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| No caching | always fresh, simple | slower, more load on Flask |
| Time-based `cacheLife` | simple, predictable | stale up to the window |
| Tag invalidation | fresh after changes, long cache life | must tag consistently and invalidate everywhere data changes |
| `updateTag` | user sees their change | only in Server Actions |
| `revalidateTag` | background refresh, cheap | brief staleness |
| Suspense streaming | fast first paint | more loading states to design |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Cache public, slowly changing data (job listings, company profiles, CMS content) with tags.
- ✅ Stream expensive or slow sections (AI results, analytics) behind Suspense.
- 🚫 Never share-cache per-user or permission-dependent data.
- 🚫 Don't cache everything "for speed" before measuring; correctness first.

## 🏆 Best practices

- [ ] Fetch independent data in parallel; avoid waterfalls.
- [ ] Wrap request-time and slow components in `<Suspense>` with meaningful fallbacks.
- [ ] Decide caching per function: public → `"use cache"` + `cacheLife` + `cacheTag`; personal → uncached.
- [ ] Tag consistently (`jobs`, `job-${id}`); invalidate in every mutation path, including webhooks from the backend.
- [ ] Use `updateTag` after user mutations in Server Actions; `revalidateTag` for background refresh.
- [ ] Don't call `cookies()`/`headers()` inside cached scopes; pass extracted values as arguments if needed.
- [ ] Verify behavior with `next build && next start` — dev mode caches differently.
- [ ] Know which model your project uses (`cacheComponents` or previous).

## 🏭 How it's used in industry

- E-commerce and job portals cache listings aggressively and invalidate on publish events.
- CMS-driven sites use webhooks to call `revalidateTag` when editors publish.
- Incidents where personalized pages were cached publicly are a known class of bug — code review checks for caching on authenticated routes.

## ⚠️ Common mistakes

- Following a Next.js 14 tutorial (`fetch` cached by default) in a Next.js 16 project.
- Caching a function that reads the session.
- Forgetting to invalidate after an update, then "fixing" it by disabling caching everywhere.
- Testing caching only in `next dev`.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a product manager why the public job list can be a few minutes stale, but a user's own saved-jobs list must be fresh and never cached across users.

## 📐 Design it

Design the fetching and caching strategy for CareerPilot's **public company page** `/companies/[id]`: company profile (edited rarely by admins), open jobs (change daily), aggregated salary stats (heavy SQL, daily), "your applications to this company" (logged-in users only), and an AI "culture summary" (slow, expensive, regenerated weekly).

:::quiz
Show a possible strategy

| Section | Fetch | Cache | Invalidation |
|---|---|---|---|
| Company profile | `getCompany(id)` | `"use cache"`, `cacheLife("days")`, `cacheTag("companies", "company-{id}")` | admin edit Server Action → `updateTag("company-{id}")`; Flask admin tool → webhook → `revalidateTag("company-{id}", "max")` |
| Open jobs | `getCompanyJobs(id)` | `cacheLife("hours")`, `cacheTag("jobs", "company-{id}-jobs")` | job published/closed → `updateTag`/`revalidateTag("company-{id}-jobs")` |
| Salary stats | `getSalaryStats(id)` | `cacheLife("days")`, `cacheTag("salary-stats")` | nightly job → `revalidateTag("salary-stats", "max")` |
| Your applications | `getMyApplicationsForCompany(session, id)` | **none** (personal) | — ; wrapped in `<Suspense>`; shows "Log in to see your applications" if no session |
| AI culture summary | `getCultureSummary(id)` | `cacheLife("weeks")`, `cacheTag("culture-{id}")` | weekly regeneration job → `revalidateTag`; rendered in its own `<Suspense>` with a skeleton |

Page structure: profile + jobs + stats in the prerendered/cached shell (fetched in parallel), personal and AI sections streamed separately so neither blocks the others. `generateMetadata` reuses the cached `getCompany`. Verified with `next build && next start` and by checking that two different test users never see each other's section.
:::

### 📝 Self-review checklist

- [ ] Public vs personal separated
- [ ] Every cached function has a lifetime and tags
- [ ] Every mutation path invalidates
- [ ] Slow sections streamed independently

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w4/06-caching" ai="no-ai" title="Cache public data, stream personal data, invalidate after mutations"}
Enable Cache Components, cache public job functions with `"use cache"`, `cacheLife` and tags, keep personal applications uncached behind `<Suspense>` reading cookies, and write a Server Action that checks the session and calls `updateTag` only after a successful mutation.
:::

:::hints
- `"use cache";` must be the **first statement** in the function body.
- `cacheTag("jobs", \`job-${id}\`)` accepts several tags.
- In the page, render `<JobList />` directly and `<MyApplicationsSummary />` inside `<Suspense fallback={…}>`.
:::

## ✅ Quick check

:::quiz
With `cacheComponents: true`, what happens to a `fetch` inside a Server Component with no `"use cache"`?

It runs at request time (dynamic). If it's outside a `<Suspense>` boundary, Next.js warns/errors so you either cache it or stream it.
:::

:::quiz
`updateTag` vs `revalidateTag`?

`updateTag` (Server Actions only) expires the cache immediately so the user sees their change; `revalidateTag` marks it stale and refreshes in the background (stale-while-revalidate), usable in Route Handlers too.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Caching | Penyimpanan sementara hasil (cache) |
| Revalidation | Validasi ulang / penyegaran cache |
| Stale-while-revalidate | Sajikan data lama sambil memperbarui di latar |
| Streaming | Mengirim halaman bertahap |
| Waterfall | Permintaan berurutan yang memperlambat |
| Cache key | Kunci cache (penentu entri cache) |

## 📚 Keep learning

- Next.js docs (bundled): Fetching Data; Caching; Revalidating; `use cache`, `cacheLife`, `cacheTag`, `updateTag` references; Caching (Previous Model)
- [React docs: Suspense](https://react.dev/reference/react/Suspense)

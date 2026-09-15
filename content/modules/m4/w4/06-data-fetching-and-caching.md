---
title: "🔥 Data Fetching & Caching in Next.js 16"
summary: Load data on the server without waiting in line, show slow parts later with Suspense, and cache on purpose with Cache Components — use cache, cacheLife, cacheTag, updateTag and revalidateTag — without leaking personal data.
type: lesson
source: original
roles: { be: recommended, fe: core, fs: core, ai: recommended, ops: recommended }
durationMinutes: 180
tags: [nextjs, caching, suspense, streaming, use-cache, performance]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Loading data in parallel instead of one after another
- Showing slow parts later with `<Suspense>` (streaming)
- **Cache Components**: fresh by default, cache only what you choose
- `"use cache"`, `cacheLife` and `cacheTag`
- Refreshing the cache after a change: `updateTag`, `revalidateTag`
- Why personal data must never be shared from the cache
- The older caching model you'll see in tutorials

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Cache** | A saved copy of a result, reused so you don't redo the work | Salinan simpanan |
| **Waterfall** | Requests waiting in line one after another, making the page slow | Antrean request |
| **Streaming** | Sending the page in pieces: fast parts first, slow parts later | Kirim bertahap |
| **`<Suspense>`** | Shows a placeholder until a slow part is ready | Penanda "tunggu" |
| **Stale** | Old but still usable data | Data lama |
| **Revalidate / invalidate** | Mark a cached copy as old so it gets refreshed | Menyegarkan cache |
| **Cache tag** | A label on cached data, so you can refresh everything with that label | Label cache |
| **Cache key** | What makes two cached entries different (for example, the job id) | Kunci cache |

## 🧠 The big idea

Caching is like a **warung that prepares popular dishes in the morning**. Nasi goreng that everyone orders (the public job list) can be prepared ahead and served instantly, and refreshed every hour. But a dish made for **one customer's allergy** (their own applications) must be cooked fresh just for them — giving it to someone else is a disaster.

The skill is labeling each dish correctly, and throwing away prepared dishes when the recipe changes (invalidation).

## ❓ Why it matters

Building every page from scratch and calling Flask on every request is slow and expensive when many people use your app. But showing old or wrong data is even worse. Next.js lets you decide **per function or component**: what can be reused, for how long, and how to refresh it after a change.

What goes wrong without a plan:
- **Waterfall**: `await getUser()`, then `await getApplications()`, then `await getStats()` — three times slower than needed.
- A slow AI endpoint blocks the whole dashboard.
- **Cached personal data**: user A sees user B's applications — a privacy incident.
- An edited job doesn't show up because nobody refreshed the cache.

:::note[Which Next.js caching model?]
Next.js 16 introduced **Cache Components**, turned on with `cacheComponents: true` in `next.config.ts`. This lesson teaches that model (the one the Next.js docs start with). Projects without that setting use the **older model** (step 8). Check `next.config.ts` before following advice from a tutorial.
:::

## 📖 Step by step

### 1. Parallel, not one by one

```tsx
// ❌ waterfall
const user = await getUser();
const applications = await getApplications();

// ✅ start together, await together
const [user, applications] = await Promise.all([getUser(), getApplications()]);
```

Like ordering food and drinks at the same time instead of waiting for the food before ordering the drink. One after another is only right when a request **needs the result** of the previous one.

### 2. Show slow parts later

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

- The heading appears immediately. Each `<Suspense>` shows its placeholder until that part is ready.
- The slow AI card doesn't hold up the stats — like a restaurant bringing each dish when it's ready instead of waiting for the slowest one.
- `loading.tsx` wraps the whole page; `<Suspense>` lets you choose smaller parts.

### 3. Turn on Cache Components

```ts
// next.config.ts
import type { NextConfig } from "next";
const nextConfig: NextConfig = { cacheComponents: true };
export default nextConfig;
```

With it:
- Data loading is **fresh (dynamic) by default**. Nothing is cached unless you say so.
- Next.js builds a ready-made **shell** of the page and streams the fresh parts into it.
- If uncached data is not inside `<Suspense>`, Next.js shows a helpful error telling you to wrap it or cache it.

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

- `"use cache"` = "save the result of this function".
- `cacheLife("hours")` = how long it stays fresh — like the "best before" label on food.
- `cacheTag("jobs")` = a label, so you can throw away every saved copy labeled `jobs` later.
- The arguments (like `id`) automatically make separate entries: job 1 and job 2 are cached separately.

| Profile | stale | revalidate | expire |
|---|---|---|---|
| `seconds` | 30s | 1s | 60s |
| `minutes` | 5m | 1m | 1h |
| `hours` | 5m | 1h | 1d |
| `days` | 5m | 1d | 1w |
| `weeks` | 5m | 1w | 30d |
| `max` | 5m | 30d | 1y |

`"use cache"` can also go at the top of an async component or page, or at the top of a file. Always pair it with a `cacheLife`.

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

Simple rules:
- Same data for everyone → cache it, with tags.
- Different data per user → **don't** put it in a shared cache. Load it fresh, inside `<Suspense>`.
- Never call `cookies()` or `headers()` **inside** a `"use cache"` function.

### 6. Refresh the cache after a change

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

| API | Where | What it does |
|---|---|---|
| `updateTag(tag)` | Server Actions | throws the cached copy away **now** → the user immediately sees their change |
| `revalidateTag(tag, "max")` | Server Actions, Route Handlers (like a webhook from Flask) | serves the old copy while refreshing in the background |
| `revalidatePath(path)` | Server Actions, Route Handlers | refreshes a whole page when you don't know its tags |

- Refresh only **after** the change succeeded.
- When **Flask** changes data (an admin tool, another user), Flask can call a Next.js Route Handler webhook that runs `revalidateTag` — the same signed-webhook idea from Module 2 Week 5.

### 7. The browser has its own cache

`router.refresh()` reloads server data for the current page. TanStack Query caches data inside the browser (lesson 07). They are different layers — when you see old data, first ask **which layer** is holding it.

### 8. The older model (without `cacheComponents`)

- `fetch` is **not** cached by default (since Next.js 15). Turn it on with `fetch(url, { cache: "force-cache", next: { revalidate: 3600, tags: ["jobs"] } })`.
- `unstable_cache(fn, keyParts, { tags, revalidate })` for data that isn't `fetch`.
- Page settings: `export const dynamic = "force-dynamic" | "force-static"`, `export const revalidate = 3600`.

You'll see this in older projects and tutorials for Next.js 13–15.

## ⚠️ Common mistakes

- Following a Next.js 14 tutorial ("fetch is cached by default") in a Next.js 16 project.
- Caching a function that reads the user's session.
- Forgetting to refresh after an update, then "fixing" it by turning caching off everywhere.
- Testing caching only with `next dev` (it behaves differently from production).
- Caching everything "for speed" before measuring — correct data comes first.

## 🏆 Best practices

- [ ] Load independent data in parallel.
- [ ] Wrap slow and per-request parts in `<Suspense>` with good placeholders.
- [ ] Decide per function: public → `"use cache"` + `cacheLife` + `cacheTag`; personal → no cache.
- [ ] Use consistent tags (`jobs`, `job-${id}`) and refresh them in **every** place data changes, including webhooks from the backend.
- [ ] `updateTag` after user changes in Server Actions; `revalidateTag` for background refresh.
- [ ] Never call `cookies()` / `headers()` inside cached functions.
- [ ] Check caching with `next build && next start`.
- [ ] Know which model your project uses.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Using the warung idea, explain to a product manager why the public job list can be a few minutes old, but a user's own saved-jobs list must always be fresh and never shared between users.

## 📐 Design it

Plan loading and caching for CareerPilot's **public company page** `/companies/[id]`: the company profile (rarely edited by admins), open jobs (change daily), salary statistics (heavy SQL, daily), "your applications to this company" (logged-in users only), and an AI "culture summary" (slow, expensive, regenerated weekly).

:::quiz
Show a possible plan

| Section | Load with | Cache | Refresh |
|---|---|---|---|
| Company profile | `getCompany(id)` | `"use cache"`, `cacheLife("days")`, `cacheTag("companies", "company-{id}")` | admin edit Server Action → `updateTag("company-{id}")`; Flask admin tool → webhook → `revalidateTag("company-{id}", "max")` |
| Open jobs | `getCompanyJobs(id)` | `cacheLife("hours")`, `cacheTag("jobs", "company-{id}-jobs")` | job published/closed → `updateTag` / `revalidateTag("company-{id}-jobs")` |
| Salary stats | `getSalaryStats(id)` | `cacheLife("days")`, `cacheTag("salary-stats")` | nightly job → `revalidateTag("salary-stats", "max")` |
| Your applications | `getMyApplicationsForCompany(session, id)` | **none** (personal) | — ; inside `<Suspense>`; shows "Log in to see your applications" without a session |
| AI culture summary | `getCultureSummary(id)` | `cacheLife("weeks")`, `cacheTag("culture-{id}")` | weekly job → `revalidateTag`; its own `<Suspense>` with a skeleton |

- The profile, jobs and stats are loaded in parallel and form the fast, cached part of the page.
- The personal section and the AI section stream separately, so neither blocks the other.
- `generateMetadata` reuses the cached `getCompany`.
- Check with `next build && next start`, and make sure two different test users never see each other's section.
:::

### 📝 Self-review checklist

- [ ] Public and personal data are separated
- [ ] Every cached function has a lifetime and tags
- [ ] Every place that changes data refreshes the cache
- [ ] Slow sections stream on their own

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w4/06-caching" ai="no-ai" title="Cache public data, stream personal data, invalidate after mutations"}
Turn on Cache Components, cache public job functions with `"use cache"`, `cacheLife` and tags, keep personal applications uncached inside `<Suspense>` (reading cookies), and write a Server Action that checks the session and calls `updateTag` only after the change succeeds.
:::

:::hints
- `"use cache";` must be the **first line** inside the function.
- `cacheTag("jobs", \`job-${id}\`)` accepts several tags.
- In the page, render `<JobList />` directly and `<MyApplicationsSummary />` inside `<Suspense fallback={…}>`.
:::

## ✅ Quick check

:::quiz
With `cacheComponents: true`, what happens to a `fetch` in a Server Component without `"use cache"`?

It runs fresh on every request. If it's not inside `<Suspense>`, Next.js warns you so you either cache it or stream it.
:::

:::quiz
`updateTag` vs `revalidateTag`?

`updateTag` (only in Server Actions) removes the cached copy immediately, so the user sees their change. `revalidateTag` marks it old and refreshes it in the background; it also works in Route Handlers.
:::

## 📚 Keep learning

- Next.js docs (bundled): Fetching Data; Caching; Revalidating; `use cache`, `cacheLife`, `cacheTag`, `updateTag` references; Caching (Previous Model)
- [React docs: Suspense](https://react.dev/reference/react/Suspense)

# Architecture G · 04 — Where state lives: filters in the URL

> 🚫🤖 **No-AI** · ⏱️ ~90 min

The CareerPilot job search keeps its filters in `useState`. Users can't share "remote data jobs sorted by salary", the back button doesn't work, and a refresh loses everything. Move the filters into the **URL** — the right home for shareable UI state — while the search box keeps fast **local** state.

## 1. `job-filters.ts` (pure)
```ts
type JobFilters = { q: string; status: "open" | "closed" | "all"; remote: boolean; sort: "newest" | "salary"; page: number };
const DEFAULT_FILTERS: JobFilters = { q: "", status: "open", remote: false, sort: "newest", page: 1 };
```
- `parseJobFilters(input: URLSearchParams | Record<string, string | string[] | undefined>)` — works with `useSearchParams()` **and** a page's `searchParams` object:
  - each field falls back to its default when missing or invalid (`status=banana` → `"open"`); arrays use the first value
  - `q` trimmed and cut to 100 characters; `remote` is `true` only for `"1"`; `page` a positive integer
- `serializeJobFilters(filters)` → a query string **without** default values, keys in the order `q, status, remote, sort, page`, `remote` as `1`; all defaults → `""`
- round trip: `parseJobFilters(new URLSearchParams(serializeJobFilters(f)))` equals `f` for valid filters

## 2. `use-job-filters.ts` (`"use client"`)
`useJobFilters()` → `{ filters, setFilters(patch, options?: { history?: "push" | "replace" }) }`
- reads `useSearchParams()`, `usePathname()`, `useRouter()` from `next/navigation`
- merges the patch; changing **anything except `page`** resets `page` to 1
- navigates to `pathname` + `?query` (just `pathname` when the query is empty) with `{ scroll: false }` using `router.push` (default) or `router.replace`
- does nothing if the resulting URL wouldn't change

## 3. `job-filter-bar.tsx` (`"use client"`)
- **Search** input with **local** state (typing must feel instant) → after **300 ms** without typing, `setFilters({ q }, { history: "replace" })` (don't create a history entry per keystroke); when the URL's `q` changes from outside (back button), the input shows it
- **Status** select (`Open`, `Closed`, `All`), **Remote only** checkbox, **Sort** select (`Newest`, `Highest salary`) → `push`

```bash
cd exercises/web
npx vitest run architecture/g-frontend-patterns/04-where-state-lives
```

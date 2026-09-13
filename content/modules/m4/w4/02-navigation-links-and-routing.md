---
title: "Navigation: Link, Active Styling & Programmatic Routing"
summary: Move between pages the Next.js way — Link with prefetching and client-side transitions, active links with usePathname, breadcrumbs, URL search params as state, and useRouter for navigation after actions.
type: lesson
source: core
sourceRef: "M3 · W4 · L2"
roles: { be: optional, fe: core, fs: core, ai: optional, ops: none }
durationMinutes: 150
tags: [nextjs, navigation, link, userouter, search-params, url-state]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- `<Link>`: client-side transitions and prefetching (and when a plain `<a>` is right)
- Active navigation with `usePathname` and `aria-current`
- Breadcrumbs derived from the path
- **URL as state**: filters, pagination and tabs in search params with `useSearchParams` + `router.replace`
- Programmatic navigation with `useRouter` (`push`, `replace`, `back`, `refresh`) and `redirect()` on the server
- Pending feedback with `useLinkStatus` and `loading.tsx`

## 🧠 The big idea

The URL is the **address and the bookmark** of your app's state. If "applications filtered by Interview, page 2" lives only in `useState`, a refresh loses it and nobody can share the link. Put it in the URL and your app becomes linkable, refresh-safe and back-button-friendly — for free.

## ❓ Why does this exist?

A full page reload for every click (classic multi-page apps) is slow and loses client state. `<Link>` gives server-rendered apps the feel of single-page apps: it prefetches routes and swaps only what changed, keeping layouts mounted.

## 💥 What happens if we DON'T?

```tsx
<a href="/applications">Applications</a>                    // full reload: layout state lost, slower
<div onClick={() => (window.location.href = "/jobs")}>Jobs</div>   // not a link: no middle-click, no keyboard, no prefetch
const [status, setStatus] = useState("all");                // refresh → filter gone; can't share the filtered view
router.push(`/applications?status=${status}`)               // clicking filters fills history; Back cycles through filters
```

## 📖 How it works, step by step

### 1. `<Link>`

```tsx
import Link from "next/link";

<Link href="/applications">Applications</Link>
<Link href={`/applications/${application.id}`}>{application.role}</Link>
<Link href={{ pathname: "/applications", query: { status: "offer" } }}>Offers</Link>
```

- Renders a real `<a href>` (accessible, middle-click opens a tab, SEO-friendly).
- **Prefetches** routes when links enter the viewport (fully for static routes, partially for dynamic routes that have `loading.tsx`).
- **Client-side transition**: keeps shared layouts, scrolls to top, no full reload.
- Use a plain `<a>` for external sites and file downloads; `prefetch={false}` for huge link lists.

### 2. Active links

```tsx
"use client";
import { usePathname } from "next/navigation";

export function NavLinks({ links }: { links: { href: string; label: string }[] }) {
  const pathname = usePathname();
  return (
    <nav aria-label="Main">
      {links.map(({ href, label }) => {
        const active = href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);
        return (
          <Link key={href} href={href} aria-current={active ? "page" : undefined} className={cn("px-3 py-2", active && "font-semibold text-indigo-600")}>
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
```

`aria-current="page"` tells screen readers which link is current — style it with Tailwind's `aria-[current=page]:` variant so visuals follow semantics. Note the `startsWith(href + "/")` detail: `/jobsearch` must not activate `/jobs`.

### 3. Breadcrumbs

Split the pathname into segments, build cumulative hrefs, and render the last one as text with `aria-current="page"` inside `<nav aria-label="Breadcrumb"><ol>`. Use a labels map (or data from the page) for segments like ids.

### 4. Search params as state

```tsx
"use client";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

export function StatusFilter() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();            // read-only URLSearchParams

  function setStatus(value: string) {
    const params = new URLSearchParams(searchParams.toString());
    value ? params.set("status", value) : params.delete("status");
    params.delete("page");                           // new filter → back to page 1
    const query = params.toString();
    router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  return <select value={searchParams.get("status") ?? ""} onChange={(e) => setStatus(e.target.value)}>…</select>;
}
```

- `replace` for filters/sorting (don't flood history); `push` for "real" navigation the user may want to go Back to.
- The Server Component page reads the same values from its `searchParams` prop and fetches the filtered data — the URL connects client controls and server data.
- For text search, debounce updates (Week 1).

### 5. Programmatic navigation

```tsx
const router = useRouter();
router.push(`/applications/${id}`);   // navigate after a successful save
router.back();                         // Cancel button
router.refresh();                      // re-render Server Components with fresh data (keeps client state)
```

On the server (Server Components, Server Actions, Route Handlers):

```tsx
import { redirect, notFound } from "next/navigation";
if (!session) redirect("/login?next=/applications");
```

Only navigate **after** the action succeeded; on failure stay and show an error.

### 6. Pending feedback

- `loading.tsx` shows immediately for routes that render slowly.
- `useLinkStatus()` (inside a component rendered within a `<Link>`) exposes `pending` for tiny inline indicators on slow networks.

### 7. Scroll and focus

Next.js scrolls to the top on navigation. For accessibility in single-page transitions, make sure each page has a clear `<h1>`; many teams also move focus to the main heading or announce the page title after navigation.

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| URL search params | shareable, refresh-safe, back button works | strings only; must validate; long URLs |
| Component state | simple, private | lost on refresh/share |
| `router.push` | history entry | Back button noise for filters |
| `router.replace` | clean history | can't go Back to previous filter |
| Prefetching | instant navigation | extra requests; disable for huge lists |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ `<Link>` for all internal navigation.
- ✅ Search params for filters, sort, pagination, selected tab — anything worth sharing.
- 🚫 Don't put sensitive data (emails, tokens) in URLs — they're logged and shared.
- 🚫 Don't use `useRouter().push` for simple links — users lose middle-click and prefetch.

## 🏆 Best practices

- [ ] Internal links with `next/link`; external with `<a>` and `rel="noopener noreferrer"` when `target="_blank"`.
- [ ] Mark active links with `aria-current="page"`; match nested routes carefully.
- [ ] Store shareable view state in the URL; validate it on the server.
- [ ] `replace` + `scroll: false` for filter changes; reset pagination on new filters.
- [ ] Navigate after success only; show errors otherwise.
- [ ] `redirect()` for server-side auth checks; include a `next` param to return after login (validate it's a relative path).
- [ ] Add `loading.tsx` to dynamic routes for instant feedback.

## 🏭 How it's used in industry

- Job portals and e-commerce put every filter in the URL so search results can be shared and indexed.
- Libraries like `nuqs` provide typed search-param state for Next.js.
- Analytics tools track navigation through URL changes — URL state makes funnels measurable.

## ⚠️ Common mistakes

- Mutating `useSearchParams()` directly (it's read-only) — copy into `new URLSearchParams`.
- Forgetting to preserve other params when changing one.
- Open redirects: `redirect(searchParams.next)` with an absolute URL from an attacker.
- Using `window.location` for internal navigation.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a product manager why the applications filter should live in the URL, using an example of sending a filtered link to a mentor.

## 📐 Design it

Design the URL scheme and navigation for CareerPilot's **applications list**: status filter, text search, company filter, sort, pagination, and an application drawer that opens on top of the list for quick preview. Decide what goes in the path vs search params, when to use push vs replace, and how Back should behave.

:::quiz
Show a possible design

- **List**: `/applications?status=interview&q=backend&company=3&sort=-updated&page=2`
  - defaults omitted from the URL (`sort=-updated`, `page=1`)
  - `status`, `company`, `sort` changes → `router.replace`, reset `page`
  - `q` → debounced 300 ms `replace`
  - pagination → `push` (users expect Back to return to page 1) — a reasonable exception
- **Detail page**: `/applications/12` (full page, shareable, SEO-irrelevant but linkable)
- **Quick preview drawer**: `/applications?…&preview=12` → `push` so Back closes the drawer; the list stays mounted; direct visits with `preview=12` open the drawer on load. (Next.js intercepting + parallel routes can also do `/applications/12` as a modal over the list — more advanced.)
- **Server**: the list page validates every param (unknown status → ignore, page not a positive integer → 1) before calling the Flask API.
- **After moving a status** in the drawer: stay, show a toast, `router.refresh()` so the list re-fetches.
:::

### 📝 Self-review checklist

- [ ] Shareable view state in the URL, defaults omitted
- [ ] push vs replace chosen deliberately
- [ ] Back button behavior makes sense
- [ ] Server validates params

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w4/02-navigation" ai="no-ai" title="Active links, breadcrumbs and URL filters"}
Build `NavLinks` with correct active matching, `Breadcrumbs` derived from the path, a `StatusFilter` that keeps other search params and resets pagination with `router.replace`, and `SaveAndOpen` that navigates only after a successful save. Tests mock `next/navigation` to control the URL.
:::

:::hints
- `new URLSearchParams(searchParams.toString())` makes a mutable copy.
- Breadcrumb hrefs: `"/" + segments.slice(0, index + 1).join("/")`.
- In `SaveAndOpen`, `try { const { id } = await onSave(); router.push(...) } catch { … }`.
:::

## ✅ Quick check

:::quiz
When should you use `router.replace` instead of `router.push`?

When the change shouldn't create a new history entry — typically filters, sorting or search text — so Back returns to the previous page, not every intermediate filter.
:::

:::quiz
Why is `<Link>` better than a `div` with `onClick` + `router.push` for navigation?

`<Link>` renders a real anchor (keyboard, screen readers, middle-click, copy link), prefetches the route, and still does a client-side transition.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Client-side transition | Perpindahan halaman di sisi klien tanpa reload |
| Prefetching | Memuat rute lebih dulu di latar belakang |
| Search params | Parameter kueri URL |
| Breadcrumb | Jejak navigasi |
| Open redirect | Pengalihan terbuka (celah keamanan) |

## 📚 Keep learning

- Next.js docs (bundled): Linking and Navigating; `useRouter`, `usePathname`, `useSearchParams`, `useLinkStatus` references
- [WAI-ARIA: aria-current](https://www.w3.org/TR/wai-aria-1.2/#aria-current)

---
title: "Navigation: Link, Active Styling & Programmatic Routing"
summary: Move between pages the Next.js way — Link with fast page changes, highlighting the current link, breadcrumbs, keeping filters in the URL, and useRouter to navigate after an action.
type: lesson
source: core
roles: { be: optional, fe: core, fs: core, ai: optional, ops: none }
durationMinutes: 150
tags: [nextjs, navigation, link, userouter, search-params, url-state]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- `<Link>`: moving between pages without a full reload
- Highlighting the current page's link
- Breadcrumbs built from the URL
- **URL as state**: filters, pages and tabs in `?status=…`
- Navigating from code with `useRouter` and `redirect()`
- Showing that a page is loading

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **`<Link>`** | Next.js's link: changes the page without reloading everything | Link Next.js |
| **Prefetch** | Loading a page in the background before you click it | Memuat lebih dulu |
| **Client-side transition** | Only the changed part is swapped; the rest stays | Pindah halaman tanpa reload |
| **`usePathname`** | A hook that gives the current path, like `/applications` | Path saat ini |
| **Search params** | The `?key=value` part of the URL | Parameter URL |
| **`router.push` / `replace`** | Go to a URL (with / without adding a Back step) | Pindah halaman dari kode |
| **Breadcrumb** | "Home › Applications › Detail" trail | Jejak navigasi |
| **Open redirect** | A security bug: sending users to any website an attacker chooses | Pengalihan berbahaya |

## 🧠 The big idea

The URL is the **address and the bookmark** of what the user is looking at. If "applications filtered by Interview, page 2" lives only in `useState`, a refresh loses it and nobody can share it. Put it in the URL, and the view can be shared, refreshed and navigated with the Back button — for free. Like a **Google Maps link**: send it to a friend and they see exactly the same place.

## ❓ Why it matters

A full page reload on every click is slow and throws away what's on screen. `<Link>` makes page changes feel instant.

Common mistakes:

```tsx
<a href="/applications">Applications</a>                    // full reload: layout state lost, slower
<div onClick={() => (window.location.href = "/jobs")}>Jobs</div>   // not a link: no middle-click, no keyboard, no prefetch
const [status, setStatus] = useState("all");                // refresh → filter gone; can't share the filtered view
router.push(`/applications?status=${status}`)               // clicking filters fills history; Back cycles through filters
```

- A plain `<a>` for internal pages reloads everything.
- A clickable `div` isn't a real link: no keyboard, no "open in new tab".
- A filter in `useState` disappears on refresh.
- `push` for every filter click fills the Back history with filters.

## 📖 Step by step

### 1. `<Link>`

```tsx
import Link from "next/link";

<Link href="/applications">Applications</Link>
<Link href={`/applications/${application.id}`}>{application.role}</Link>
<Link href={{ pathname: "/applications", query: { status: "offer" } }}>Offers</Link>
```

- It renders a real `<a href>`: keyboard, screen readers and "open in new tab" all work.
- It **prefetches** pages when the link appears on screen, so clicking feels instant — like a waiter preparing the menu before you sit down.
- It swaps only the changed part; shared layouts stay.
- Use a plain `<a>` for other websites and file downloads.

### 2. Highlight the current link

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

- `usePathname()` gives the current path.
- `aria-current="page"` tells screen readers "you are here" — like the red dot on a mall map.
- Careful matching: `/jobsearch` must **not** highlight `/jobs`. That's why the code checks `startsWith(href + "/")`.

### 3. Breadcrumbs

Split the path into parts, build a link for each step, and show the last one as plain text with `aria-current="page"`, inside `<nav aria-label="Breadcrumb"><ol>`. Use a small labels table for parts like ids ("12" → "Backend Engineer").

### 4. Filters in the URL

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

- `useSearchParams()` is read-only, so make a copy with `new URLSearchParams(...)`.
- Keep the other params (like `q`), but reset `page` when the filter changes.
- `replace` for filters and sorting (no extra Back steps). `push` for real page changes the user may want to go Back to.
- The Server Component page reads the same values from its `searchParams` and loads the filtered data. The URL connects the browser controls and the server data.
- For a search box, wait until typing stops (debounce, Week 1).

### 5. Navigating from code

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

- Navigate only **after** the action succeeded. If it fails, stay and show an error.
- `router.refresh()` reloads the server data but keeps what's typed in the browser.
- `redirect()` is like a receptionist saying "please go to the login desk first".

### 6. Showing loading

- `loading.tsx` shows immediately for slow pages.
- `useLinkStatus()` (in a component inside a `<Link>`) gives `pending`, for a tiny spinner on slow networks.

### 7. Scroll and focus

Next.js scrolls to the top when the page changes. Make sure every page has a clear `<h1>`, so screen reader users know the page changed.

## ⚠️ Common mistakes

- Changing `useSearchParams()` directly (it's read-only) — copy it into `new URLSearchParams`.
- Losing the other params when changing one.
- **Open redirect**: `redirect(searchParams.next)` with a full URL an attacker supplied. Only allow relative paths like `/applications`.
- `window.location` for internal pages.
- Sensitive data (emails, tokens) in URLs — URLs get logged and shared.
- `router.push` in a `div` instead of a real `<Link>`.

## 🏆 Best practices

- [ ] Internal links with `next/link`; external links with `<a>` and `rel="noopener noreferrer"` when `target="_blank"`.
- [ ] Mark the current link with `aria-current="page"`; match nested pages carefully.
- [ ] Put shareable view state in the URL; check it on the server.
- [ ] `replace` + `scroll: false` for filters; reset the page number when filters change.
- [ ] Navigate only after success.
- [ ] `redirect()` for server-side login checks, with a validated `next` path.
- [ ] Add `loading.tsx` to dynamic pages.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Using the Google Maps link idea, explain to a product manager why the applications filter should live in the URL — for example, sending a filtered link to a mentor.

## 📐 Design it

Design the URL and navigation for CareerPilot's **applications list**: status filter, text search, company filter, sort, pagination, and a preview drawer that opens on top of the list. Decide what goes in the path vs the `?` part, when to use push vs replace, and how Back should behave.

:::quiz
Show a possible design

- **List**: `/applications?status=interview&q=backend&company=3&sort=-updated&page=2`
  - Default values are left out of the URL (`sort=-updated`, `page=1`).
  - Changing `status`, `company` or `sort` → `router.replace`, and reset `page`.
  - `q` (search text) → `replace` after 300 ms without typing.
  - Pagination → `push` (people expect Back to return to page 1) — a reasonable exception.
- **Detail page**: `/applications/12` — a full page that can be shared.
- **Preview drawer**: `/applications?…&preview=12` → `push`, so Back closes the drawer. The list stays on screen. Opening that link directly opens the drawer too. (Next.js "intercepting routes" can also show `/applications/12` as a modal — more advanced.)
- **Server**: the list page checks every param (unknown status → ignore; page not a positive whole number → 1) before calling the Flask API.
- **After changing a status** in the drawer: stay, show a small message, and call `router.refresh()` so the list reloads.
:::

### 📝 Self-review checklist

- [ ] Shareable view state is in the URL, defaults left out
- [ ] push vs replace chosen on purpose
- [ ] The Back button behaves as users expect
- [ ] The server checks the params

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w4/02-navigation" ai="no-ai" title="Active links, breadcrumbs and URL filters"}
Build `NavLinks` with correct current-link matching, `Breadcrumbs` built from the path, a `StatusFilter` that keeps the other URL params and resets pagination with `router.replace`, and `SaveAndOpen` that navigates only after a successful save. The tests fake `next/navigation` to control the URL.
:::

:::hints
- `new URLSearchParams(searchParams.toString())` makes a copy you can change.
- Breadcrumb links: `"/" + segments.slice(0, index + 1).join("/")`.
- In `SaveAndOpen`: `try { const { id } = await onSave(); router.push(...) } catch { … }`.
:::

## ✅ Quick check

:::quiz
When should you use `router.replace` instead of `router.push`?

When the change shouldn't add a Back step — usually filters, sorting or search text — so Back goes to the previous page, not through every filter.
:::

:::quiz
Why is `<Link>` better than a `div` with `onClick` + `router.push`?

`<Link>` is a real link (keyboard, screen readers, open in new tab, copy link), it prefetches the page, and it still changes pages without a full reload.
:::

## 📚 Keep learning

- Next.js docs (bundled): Linking and Navigating; `useRouter`, `usePathname`, `useSearchParams`, `useLinkStatus` references
- [WAI-ARIA: aria-current](https://www.w3.org/TR/wai-aria-1.2/#aria-current)

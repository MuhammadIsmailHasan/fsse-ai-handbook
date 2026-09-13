# M4 · W4 · 02 — Navigation: Active Links, Breadcrumbs and URL State

> 🚫🤖 **No-AI** · ⏱️ ~75 min · edit **`navigation.tsx`** (a Client Component file)

Use `next/link` and the hooks from `next/navigation` (`usePathname`, `useSearchParams`, `useRouter`). The tests control the current URL for you.

| Component | Requirements |
|---|---|
| `NavLinks({ links })` | `links: { href: string; label: string }[]` → `<nav aria-label="Main">` with a `Link` per item. The **active** link gets `aria-current="page"` and the class `font-semibold`. Active means: `href === "/"` only when the path is exactly `/`; otherwise the path equals `href` or starts with `href + "/"` (so `/jobs/12` activates **Jobs**, but `/jobsearch` doesn't) |
| `Breadcrumbs({ labels = {} })` | from the path `/dashboard/applications/12`: `<nav aria-label="Breadcrumb"><ol>` with `Home` → `/`, `Dashboard` → `/dashboard`, `Applications` → `/dashboard/applications`, and the last item `12` as plain text with `aria-current="page"` (not a link). Segment names: `labels[segment]` if given, else the segment with the first letter capitalized and `-` replaced by spaces. On `/` render nothing |
| `StatusFilter()` | a `<select>` labelled `Status` with options `All` (`""`), `Saved`, `Applied`, `Interview`, `Offer`, `Rejected` (lower-case values). Its value comes from the `status` search param. On change: keep the other params, set or delete `status`, **delete `page`** (back to page 1), and call `router.replace()` with `"{pathname}?{params}"` — or just `pathname` when no params remain. Use `{ scroll: false }` |
| `SaveAndOpen({ onSave })` | a button `Save and open`. On click: disable it, `await onSave()` (returns `{ id }`), then `router.push("/applications/{id}")`. If `onSave` throws, re-enable the button, show `<p role="alert">Couldn't save. Try again.</p>` and **don't** navigate. Also a `Back` button calling `router.back()` |

```bash
cd exercises/web
npx vitest run m4/w4/02-navigation
```

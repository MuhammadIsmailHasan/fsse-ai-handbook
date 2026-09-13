# M4 · W2 · 05 — Responsive Job Cards with Tailwind Utilities

> 🚫🤖 **No-AI** · ⏱️ ~60 min · edit **`job-list.html`**

`app.css` (provided) loads Tailwind. Style `job-list.html` **only with utility classes** (no `style=""`, no custom CSS, no arbitrary values like `w-[437px]`). Open it in a browser with a Tailwind build, or just iterate with the tests.

| Element | Classes it must have |
|---|---|
| `<main>` | centered container: `mx-auto`, a `max-w-*` (`4xl`/`5xl`/`6xl`), `px-4` |
| `<h1>` | `text-2xl`, `font-bold`, `tracking-tight`, and a larger size from `sm:` (e.g. `sm:text-3xl`) |
| `<ul>` | `grid`, a `gap-*`, `sm:grid-cols-2`, `lg:grid-cols-3` |
| each `<article>` card | `rounded-xl`, `border`, `border-slate-200`, `bg-white`, `p-4`, `shadow-sm`, plus `dark:border-slate-800` and `dark:bg-slate-900`; `flex flex-col` so the button sits at the bottom |
| card `<h2>` | `text-lg`, `font-semibold` |
| description `<p>` | `line-clamp-2`, `text-sm`, `text-slate-600`, `dark:text-slate-300` |
| status badge `<span>` | `inline-flex`, `items-center`, `rounded-full`, `px-2`, `py-0.5`, `text-xs`, `font-medium` |
| `<button>` | `mt-auto`, `rounded-lg`, `bg-indigo-600`, `px-4`, `py-2`, `text-white`, `hover:bg-indigo-500`, `focus-visible:outline-2`, `focus-visible:outline-offset-2`, `focus-visible:outline-indigo-600`, `disabled:opacity-50` |

There are three cards; keep the text content as is. The tests also compile Tailwind to confirm every class generates CSS (a typo like `sm:grid-col-2` fails).

```bash
cd exercises/web
npx vitest run m4/w2/05-tailwind-components
```

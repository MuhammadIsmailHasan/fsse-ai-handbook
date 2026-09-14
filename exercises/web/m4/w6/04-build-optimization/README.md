# M4 · W6 · 04 — Build optimization: fix a slow job page

> 🚫🤖 **No-AI** · ⏱️ ~90 min

The CareerPilot job page works, but Lighthouse is unhappy: a render-blocking Google Fonts `<link>`, unoptimized `<img>` tags, a chart library in the first-load bundle, and a markdown parser shipped to every visitor. Refactor it.

Provided and **not** to be edited: `lib/markdown.ts` (pretend it's a 90 KB parser), `components/salary-chart.tsx` (pretend it's a 200 KB chart library, browser-only), `lib/jobs.ts`.

## 1. `next.config.ts`
- `images.remotePatterns`: allow **only** `https://cdn.careerpilot.app/logos/**` (use `new URL(...)`)
- `images.formats`: `["image/avif", "image/webp"]`
- `poweredByHeader: false` (don't advertise the framework)

## 2. `app/layout.tsx` — fonts
Replace the Google Fonts `<link>` with **`next/font/google`**: `Inter({ subsets: ["latin"], display: "swap", variable: "--font-sans" })`, and put `inter.variable` in the `<html>` `className`. (Self-hosted at build time, no layout shift, no request to Google from the browser.)

## 3. `app/jobs/[id]/page.tsx` — images and bundles
- Replace both `<img>` tags with **`next/image`**:
  - company logo: `width={64} height={64}` and `alt="{company} logo"`
  - banner (above the fold, it's the LCP element): `width={1200} height={400}`, `alt=""` is **not** OK here → `alt="{title} at {company}"`, and **`preload`** (Next.js 16 replaced `priority` with `preload`) plus `sizes="100vw"`
- Render the description with `<JobDescription markdown={job.description} />` (a Server Component)
- Render the chart with `<SalaryChartLazy points={job.salaryPoints} />`

## 4. `components/job-description.tsx`
Currently a Client Component for no reason. Remove `"use client"` and the state; it just renders `renderMarkdown(markdown)` via `dangerouslySetInnerHTML` inside `<div className="prose">`.

## 5. `components/salary-chart-lazy.tsx` (new, `"use client"`)
`SalaryChartLazy` = `dynamic(() => import("./salary-chart"), { ssr: false, loading: () => <p>Loading salary chart…</p> })`. The chart code is then downloaded only in the browser, after the page is usable.

> Rule the grader enforces: no `"use client"` file may statically import `lib/markdown` or `components/salary-chart`.

```bash
cd exercises/web
npx vitest run m4/w6/04-build-optimization
```
In a real project, confirm with `npm run build` (route sizes), `npx next experimental-analyze` and Lighthouse.

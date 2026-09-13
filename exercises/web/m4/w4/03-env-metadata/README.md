# M4 · W4 · 03 — Environment Variables & Metadata

> 🚫🤖 **No-AI** · ⏱️ ~60 min

## 1. `lib/env.ts`
| Export | Requirements |
|---|---|
| `readServerEnv(env = process.env)` | returns `{ apiUrl, apiToken, appEnv }` from `API_URL`, `API_TOKEN`, `APP_ENV`. `API_URL` must be an `http(s)://` URL (trailing `/` removed); `API_TOKEN` at least 20 characters; `APP_ENV` one of `development`/`test`/`production` (default `development`). Collect **all** problems and throw one `Error` whose message lists the variable **names** (never the values) |
| `publicEnv` | `{ apiUrl, appName }` from `NEXT_PUBLIC_API_URL` (default `"http://localhost:5091"`) and `NEXT_PUBLIC_APP_NAME` (default `"CareerPilot"`). Write each as a **literal** `process.env.NEXT_PUBLIC_...` reference — Next.js inlines only literal references into the browser bundle (a test checks) |

## 2. `.env.example`
Commit an example with `API_URL`, `API_TOKEN`, `APP_ENV`, `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_APP_NAME`. `API_TOKEN` must be a placeholder (like `change-me`), not a real-looking secret.

## 3. Metadata
- `app/layout.tsx`: export `metadata: Metadata` with `metadataBase: new URL("https://careerpilot.id")`, `title: { default: "CareerPilot", template: "%s · CareerPilot" }`, a non-empty `description`, and `openGraph: { siteName: "CareerPilot", locale: "id_ID", type: "website" }`. The layout component renders `<html lang="en"><body>{children}</body></html>`
- `app/jobs/[id]/page.tsx`: export `generateMetadata({ params })` using the provided `getJob`:
  - found → `title: job.title`, `description: "{title} at {company} in {city}"`, `alternates: { canonical: "/jobs/{id}" }`, `openGraph: { title, description, url: "/jobs/{id}" }`
  - not found → `title: "Job not found"`, `robots: { index: false }`
  - plus a default export page that shows `<h1>{title}</h1>` (or calls `notFound()`)

```bash
cd exercises/web
npx vitest run m4/w4/03-env-metadata
```

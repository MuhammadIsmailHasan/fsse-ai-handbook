# M4 · W4 · 05 — Server and Client Components: Split a "use client" Page

> 🚫🤖 **No-AI** · ⏱️ ~75 min

`app/jobs/[id]/page.tsx` was written as one big Client Component. It fetches in `useEffect` with a **secret token** (which ships to every browser), shows a loading flash, and sends all its code to the client. Refactor it into Server Components with small client islands. Keep the same files listed below (create the missing ones).

| File | Kind | Requirements |
|---|---|---|
| `lib/data.ts` | server-only | `import "server-only"` at the top. `getJob(id: number)` calls `fetch("{API_URL}/api/v1/jobs/{id}", { headers: { Authorization: "Bearer {API_TOKEN}" } })` using `process.env.API_URL` and `process.env.API_TOKEN`; returns the `data` object or `null` on 404 |
| `app/jobs/[id]/page.tsx` | **Server** (no `"use client"`, no hooks) | `async`, awaits `params`, `getJob(Number(id))`, `notFound()` if missing. Renders `<article>` with `<h1>{title}</h1>`, `<p>{company}</p>`, `<JobDescription text={description} />`, `<SaveJobButton jobId={id} initialSaved={saved} />` and `<ShareButton url={"https://careerpilot.id/jobs/" + id} />` |
| `app/jobs/[id]/job-description.tsx` | **Server** | splits `text` on blank lines into `<p>` paragraphs (no client JS needed) |
| `app/jobs/[id]/save-job-button.tsx` | **Client** | `useState(initialSaved)`; a `<button aria-pressed>` `Save job` / `Saved`; on click it flips the state and calls `saveJob(jobId, nextSaved)` from `lib/client-api.ts` (provided); if that rejects, it flips back |
| `app/jobs/[id]/share-button.tsx` | **Client** | button `Copy link` → `navigator.clipboard.writeText(url)` → text becomes `Link copied` |

Rules the tests check: client files start with `"use client"`, don't import `lib/data`, and don't read non-public `process.env`; the page passes only **serializable** props (no functions) to client components.

```bash
cd exercises/web
npx vitest run m4/w4/05-server-client-components
```

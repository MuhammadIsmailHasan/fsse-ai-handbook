---
title: "Environment Variables & Metadata"
summary: Configure Next.js safely — server-only vs NEXT_PUBLIC_ variables, .env files, checking settings at startup — and make pages look good when shared or searched, with page titles and link previews.
type: lesson
source: core
roles: { be: optional, fe: core, fs: core, ai: recommended, ops: recommended }
durationMinutes: 120
tags: [nextjs, environment-variables, security, metadata, seo, open-graph]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- `.env` files: which ones exist and which to commit
- Server-only variables vs `NEXT_PUBLIC_` variables
- Keeping secrets away from the browser
- Checking settings when the app starts
- Page titles and descriptions with the Metadata API
- Link previews (Open Graph), sitemap and robots

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Environment variable** | A setting outside your code, like `API_URL`, that differs per computer or server | Variabel lingkungan |
| **`.env` file** | A text file that holds environment variables | File pengaturan |
| **Secret** | A value that must stay private: tokens, passwords, keys | Rahasia |
| **`NEXT_PUBLIC_`** | A prefix that copies a variable into browser code — public! | Awalan untuk publik |
| **Build time** | When `next build` creates the app files | Saat build |
| **Metadata** | Information about a page: title, description, preview image | Informasi halaman |
| **Open Graph** | Tags that control link previews on WhatsApp, LinkedIn… | Pratinjau tautan |
| **BFF (Backend for Frontend)** | Your Next.js server calls the API for the browser and adds the secrets | Server perantara |

## 🧠 The big idea

Environment variables come in two kinds:
- **House keys** — API tokens, database URLs. They stay inside the house (the server).
- **The house number** — the public site URL, an analytics id. It's painted on the gate for everyone.

The `NEXT_PUBLIC_` prefix is like **painting a value on the gate**: once the app is built, every visitor can read it.

Metadata is your **shop sign and business card**: the title in the browser tab, the preview card on WhatsApp and LinkedIn, and what Google shows.

## ❓ Why it matters

- The same app runs on your laptop (Flask on `localhost:5091`), on a staging server and in production — with different URLs and keys.
- A shared job link without Open Graph tags shows a blank card on LinkedIn, so nobody clicks it.

A dangerous mistake:

```ts
// app/applications/client-list.tsx ("use client")
fetch(`${process.env.NEXT_PUBLIC_API_URL}/applications`, {
  headers: { Authorization: `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}` },   // 🚨 token inlined into public JS
});
```

Anyone can open DevTools → Sources and read the token. And if `API_URL` is missing in production, requests silently go to `"undefined/api/v1/..."`.

## 📖 Step by step

### 1. The `.env` files

| File | Commit it? | Used when |
|---|---|---|
| `.env` | usually no (only non-secret defaults) | always |
| `.env.local` | **never** | always (overrides `.env`); not in tests |
| `.env.development` / `.env.production` | only non-secret defaults | `next dev` / `next build` + `next start` |
| `.env.example` | **yes** — a list of variables with fake values | never loaded |

- Real variables set on the server (Vercel settings, Docker `-e`, CI secrets) win over files.
- `create-next-app` ignores `.env*` in git. Add `!.env.example` to `.gitignore` so the example file is committed — it's the **instruction sheet** for teammates.

### 2. Server vs public

```bash
# .env.local
API_URL=http://localhost:5091           # server only
API_TOKEN=change-me                     # server only — secret
NEXT_PUBLIC_API_URL=http://localhost:5091   # inlined into browser JS at build time
```

- Without the prefix, a variable exists **only on the server** (Server Components, Route Handlers, Server Actions).
- With `NEXT_PUBLIC_`, the value is **copied into the JavaScript files during `next build`** — like printing it into a book. Change it later → you must rebuild (print again).
- Watch out: a Docker image built once for staging and then moved to production still has the **staging** value printed inside.
- Only direct references are copied: `process.env.NEXT_PUBLIC_API_URL` ✅, `process.env[name]` ❌.

### 3. Keep secrets on the server

```ts
// lib/data.ts
import "server-only";                  // importing this from a Client Component → build error

export async function getApplications(token: string) {
  return fetch(`${process.env.API_URL}/api/v1/applications`, { headers: { Authorization: `Bearer ${token}` } });
}
```

- `import "server-only"` is a lock: if a Client Component imports this file, the build fails.
- When browser code needs protected data, it asks **your Next.js server** (a Route Handler or Server Action). The server adds the secret and calls Flask. This is the **BFF** pattern — like a bank teller who uses the vault key for you, instead of giving you the key.

### 4. Check settings at startup

```ts
export function readServerEnv(env = process.env) {
  const problems: string[] = [];
  if (!/^https?:\/\//.test(env.API_URL ?? "")) problems.push("API_URL must be an http(s) URL");
  if ((env.API_TOKEN ?? "").length < 20) problems.push("API_TOKEN must be at least 20 characters");
  if (problems.length) throw new Error(`Invalid environment:\n- ${problems.join("\n- ")}`);
  return { apiUrl: env.API_URL!.replace(/\/+$/, ""), apiToken: env.API_TOKEN! };
}
```

- Stop immediately with a clear message when a setting is missing or wrong — like a pilot's pre-flight check.
- Show **names, never values** (a secret in an error log is a leak).
- Same idea as Module 2 Week 6, now in TypeScript. (Zod makes this shorter — Week 5.)

### 5. Page titles

```tsx
// app/layout.tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  metadataBase: new URL("https://careerpilot.id"),   // makes relative URLs absolute
  title: { default: "CareerPilot", template: "%s · CareerPilot" },
  description: "Track job applications and prepare for interviews with AI.",
  openGraph: { siteName: "CareerPilot", locale: "id_ID", type: "website" },
};
```

- `title.template`: a page with `title: "Applications"` shows `Applications · CareerPilot` in the tab.
- `title.default`: used when a page sets no title.
- `metadataBase`: turns relative URLs (like `/jobs/1`) into full URLs for previews.

### 6. Titles from data: `generateMetadata`

```tsx
// app/jobs/[id]/page.tsx
export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const job = await getJob(Number(id));
  if (!job) return { title: "Job not found", robots: { index: false } };
  const description = `${job.title} at ${job.company} in ${job.city}`;
  return {
    title: job.title,
    description,
    alternates: { canonical: `/jobs/${id}` },
    openGraph: { title: job.title, description, url: `/jobs/${id}` },
  };
}
```

- Each job page gets its own title and preview — like a name card for each product on a shelf.
- `canonical` = "this is the main address of this page" (helps Google).
- `robots: { index: false }` = "don't show this page in Google".
- Metadata only works in **Server Components**.

### 7. Special metadata files

| File in `app/` | Creates |
|---|---|
| `favicon.ico`, `icon.png`, `apple-icon.png` | the site icons |
| `opengraph-image.png` or `opengraph-image.tsx` | the link preview image |
| `sitemap.ts` | `/sitemap.xml` (a list of pages for Google) |
| `robots.ts` | `/robots.txt` (which pages Google may visit) |

Private pages (the dashboard) should not be indexed. Public job pages should be in the sitemap.

## ⚠️ Common mistakes

- `NEXT_PUBLIC_API_KEY=sk-live-…` — a secret made public.
- Changing a `NEXT_PUBLIC_` value and expecting it to work without rebuilding.
- Putting `.env` files inside `src/` (Next.js reads them from the project root).
- Committing `.env.local`.
- Relative preview image URLs without `metadataBase`.
- Letting Google index private or empty pages.

## 🏆 Best practices

- [ ] Commit `.env.example`; never commit `.env.local` or real secrets.
- [ ] Use secrets only in server code; add `import "server-only"` to data files.
- [ ] Check environment variables at startup, with names but no values in errors.
- [ ] Remember `NEXT_PUBLIC_` values are fixed at build time — plan builds per environment.
- [ ] Root `metadata` with `metadataBase`, a title template and a description; `generateMetadata` for dynamic pages.
- [ ] Add preview images, `sitemap.ts` and `robots.ts`; `noindex` for private and not-found pages.
- [ ] Test link previews with LinkedIn's Post Inspector before launch.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Using the house-keys-vs-house-number idea, explain to a teammate why `NEXT_PUBLIC_API_TOKEN` is a security problem even though "you have to log in", and what the BFF pattern changes.

## 📐 Design it

CareerPilot's frontend is built once as a Docker image and then moved from staging to production. It needs: the public site URL, the Flask API URL, an analytics id, a secret API service token, and an "AI match enabled" feature flag. Decide which variables exist, their prefixes, how the browser gets values that differ per environment **without rebuilding**, and how to check them.

:::quiz
Show a possible design

| Variable | Kind | Why |
|---|---|---|
| `SITE_URL` | server | used in `metadataBase`, sitemap, emails |
| `API_URL` | server | Server Components / Route Handlers call Flask |
| `API_SERVICE_TOKEN` | server, secret | server-to-server calls; never in the browser |
| `ANALYTICS_ID` | server → given to the browser at runtime | differs per environment; the image is built once |
| `FEATURE_AI_MATCH` | server → given to the browser at runtime | the flag differs per environment |

- **No `NEXT_PUBLIC_` variables**, because the same image moves to production: values printed at build time would keep staging values forever.
- **How the browser gets them**: the root layout (a Server Component) reads `ANALYTICS_ID` and `FEATURE_AI_MATCH` and passes them as props to a small client `ConfigProvider`. Or a `GET /api/config` Route Handler returns only the public values.
- **Browser data requests** go through Route Handlers (BFF), which add the user's session and call `API_URL`.
- **Checks** in `lib/env.ts` (server-only), run at startup: URLs must be http(s), the token must be at least 32 characters in production, flags must be `"true"` or `"false"`. Errors list names only. `.env.example` documents everything with fake values.
:::

### 📝 Self-review checklist

- [ ] Secrets never reach the browser
- [ ] "Build once, deploy to many environments" is handled
- [ ] Checks without leaking values

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w4/03-env-metadata" ai="no-ai" title="Validated env config and page metadata"}
Write a server env reader that stops early with clear errors, a browser-safe `publicEnv` with direct `NEXT_PUBLIC_` references, document the variables in `.env.example`, and add root metadata with a title template plus `generateMetadata` for a dynamic job page (including a not-found version with `noindex`).
:::

:::hints
- Collect problems in an array; throw once, with only the names in the message.
- `metadataBase: new URL("https://careerpilot.id")`.
- `generateMetadata` receives the same `params` Promise as the page.
:::

## ✅ Quick check

:::quiz
When is the value of `process.env.NEXT_PUBLIC_API_URL` fixed for browser code?

At build time (`next build`) — it's replaced with the actual text inside the JavaScript files.
:::

:::quiz
What does `title.template` in the root layout do?

It formats the titles of child pages. `"%s · CareerPilot"` turns a page title "Jobs" into "Jobs · CareerPilot". `title.default` is used when a page sets no title.
:::

## 📚 Keep learning

- Next.js docs (bundled): Environment Variables guide; Metadata and OG images; `generateMetadata` reference
- [Open Graph protocol](https://ogp.me/)

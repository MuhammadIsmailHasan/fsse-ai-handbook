---
title: "Environment Variables & Metadata"
summary: Configure Next.js safely — server-only vs NEXT_PUBLIC_ variables, .env files and build-time inlining, validating config — and make pages shareable and discoverable with the Metadata API, title templates and Open Graph.
type: lesson
source: core
sourceRef: "M3 · W4 · L3"
roles: { be: optional, fe: core, fs: core, ai: recommended, ops: recommended }
durationMinutes: 120
tags: [nextjs, environment-variables, security, metadata, seo, open-graph]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- `.env`, `.env.local`, `.env.development`, `.env.production` — load order and what to commit
- **Server-only** variables vs **`NEXT_PUBLIC_`** variables inlined at **build time**
- Keeping secrets on the server: `server-only`, Server Components, Route Handlers
- Validating configuration at startup (connect to Module 2 Week 6)
- The **Metadata API**: static `metadata`, `generateMetadata`, title templates, `metadataBase`, Open Graph, canonical URLs, robots
- Metadata files: `favicon.ico`, `opengraph-image`, `sitemap.ts`, `robots.ts`

## 🧠 The big idea

Environment variables come in two kinds: **house keys** (API tokens, database URLs — stay inside the house, i.e. the server) and **the house number** (the public API URL, analytics id — printed on the door for everyone). The `NEXT_PUBLIC_` prefix is literally painting a value on the door: once built, every visitor can read it.

Metadata is the **shop sign and business card**: the title in the tab, the preview card on WhatsApp and LinkedIn, and what search engines show.

## ❓ Why does this exist?

- The same app runs locally (Flask on `localhost:5091`), in staging and in production with different URLs and keys.
- Bundlers can only give browser code values that exist at build time.
- A shared job link on LinkedIn without Open Graph tags shows a blank card — nobody clicks it.

## 💥 What happens if we DON'T?

```ts
// app/applications/client-list.tsx ("use client")
fetch(`${process.env.NEXT_PUBLIC_API_URL}/applications`, {
  headers: { Authorization: `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}` },   // 🚨 token inlined into public JS
});
```

Anyone can open DevTools → Sources and read the token. And a missing `API_URL` in production silently becomes `"undefined/api/v1/..."` requests.

## 📖 How it works, step by step

### 1. Files and precedence

| File | Committed? | Loaded when |
|---|---|---|
| `.env` | usually no (can hold non-secret defaults) | always |
| `.env.local` | **never** | always (overrides `.env`); not loaded in `test` |
| `.env.development` / `.env.production` | only non-secret defaults | `next dev` / `next build` + `next start` |
| `.env.example` | **yes** — documentation with placeholders | never loaded |

Real platform environment variables (Vercel settings, Docker `-e`, CI secrets) override files. `create-next-app` adds `.env*` to `.gitignore` — add `!.env.example` so the example is committed.

### 2. Server vs public

```bash
# .env.local
API_URL=http://localhost:5091           # server only
API_TOKEN=change-me                     # server only — secret
NEXT_PUBLIC_API_URL=http://localhost:5091   # inlined into browser JS at build time
```

- Unprefixed variables exist only in Node.js (Server Components, Route Handlers, Server Actions, `proxy.ts`).
- `NEXT_PUBLIC_` variables are **replaced by their value during `next build`**. Changing them later requires a rebuild — a Docker image built once and promoted from staging to production keeps the staging value!
- Only **literal** references are inlined: `process.env.NEXT_PUBLIC_API_URL` ✅, `process.env[name]` ❌.

### 3. Keep secrets server-side

```ts
// lib/data.ts
import "server-only";                  // importing this from a Client Component → build error

export async function getApplications(token: string) {
  return fetch(`${process.env.API_URL}/api/v1/applications`, { headers: { Authorization: `Bearer ${token}` } });
}
```

Browser code that needs protected data calls **your** Next.js server (a Route Handler or Server Action), which adds the secret and forwards to Flask — the **Backend for Frontend** pattern.

### 4. Validate configuration

```ts
export function readServerEnv(env = process.env) {
  const problems: string[] = [];
  if (!/^https?:\/\//.test(env.API_URL ?? "")) problems.push("API_URL must be an http(s) URL");
  if ((env.API_TOKEN ?? "").length < 20) problems.push("API_TOKEN must be at least 20 characters");
  if (problems.length) throw new Error(`Invalid environment:\n- ${problems.join("\n- ")}`);
  return { apiUrl: env.API_URL!.replace(/\/+$/, ""), apiToken: env.API_TOKEN! };
}
```

Fail fast with **names, never values** in the message — exactly the Module 2 Week 6 lesson, in TypeScript. (Zod makes this declarative — Week 5.)

### 5. Static metadata and title templates

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

A child page with `title: "Applications"` renders `<title>Applications · CareerPilot</title>`. The template applies to **child** segments.

### 6. `generateMetadata` for data-driven pages

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

Metadata exports only work in **Server Components**. Calling `getJob` in both `generateMetadata` and the page is fine — deduplicate with `use cache` or React's `cache()` for non-fetch data sources.

### 7. Metadata files

| File in `app/` | Produces |
|---|---|
| `favicon.ico`, `icon.png`, `apple-icon.png` | icon tags |
| `opengraph-image.png` or `opengraph-image.tsx` | Open Graph image (can be generated with `ImageResponse`) |
| `sitemap.ts` | `/sitemap.xml` |
| `robots.ts` | `/robots.txt` |

Private areas (dashboard) should be `noindex`; public job pages should be in the sitemap.

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| `NEXT_PUBLIC_` | available in browser code | frozen at build time; public |
| Server-only env + BFF | secrets safe, can change without rebuild | extra hop through the Next.js server |
| Runtime config endpoint | one image for all environments | extra request; more code |
| Static metadata | simple, fast | same for every page in the segment |
| `generateMetadata` | per-resource titles and previews | data fetching for metadata |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ `NEXT_PUBLIC_` only for truly public values (public API base URL, analytics ids, feature flags safe to expose).
- ✅ Metadata on every public page; Open Graph for shareable pages.
- 🚫 Never put tokens, keys or internal URLs you don't want public in `NEXT_PUBLIC_`.
- 🚫 Don't index private or empty pages.

## 🏆 Best practices

- [ ] Commit `.env.example`; never commit `.env.local` or real secrets.
- [ ] Access secrets only in server code; add `import "server-only"` to data modules.
- [ ] Validate env vars at startup with helpful messages (no values).
- [ ] Remember `NEXT_PUBLIC_` values are fixed at build time — plan Docker/CI builds per environment.
- [ ] Root `metadata` with `metadataBase`, title template and description; `generateMetadata` for dynamic pages.
- [ ] Canonical URLs, Open Graph images, `sitemap.ts`/`robots.ts`; `noindex` for private and not-found pages.
- [ ] Test link previews with LinkedIn's Post Inspector or similar tools before launch.

## 🏭 How it's used in industry

- Platforms like Vercel and Netlify manage environment variables per environment (development, preview, production) and warn when secrets use public prefixes.
- Job portals depend on structured metadata and sitemaps for Google Jobs and social sharing.
- Security reviews grep builds for leaked keys; secret scanning (Module 2 Week 6) runs on frontend repos too.

## ⚠️ Common mistakes

- `NEXT_PUBLIC_API_KEY=sk-live-…`.
- Expecting a changed `NEXT_PUBLIC_` value to apply without rebuilding.
- `.env` files inside `src/` (Next.js loads them from the project root).
- Relative Open Graph image URLs without `metadataBase`.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a teammate why `NEXT_PUBLIC_API_TOKEN` is a security incident even though "the site requires login", and what architecture fixes it.

## 📐 Design it

CareerPilot's frontend is built once as a Docker image and promoted from staging to production. It needs: the public site URL, the Flask API URL (server calls), an analytics id, a server-side API service token, and a feature flag "AI match enabled". Design which variables exist, their prefixes, how the browser learns values that differ per environment without rebuilding, and the validation.

:::quiz
Show a possible design

| Variable | Kind | Why |
|---|---|---|
| `SITE_URL` | server | used in `metadataBase`, sitemap, emails |
| `API_URL` | server | Server Components / Route Handlers call Flask |
| `API_SERVICE_TOKEN` | server, secret | service-to-service calls; never in the browser |
| `ANALYTICS_ID` | server → exposed at runtime | differs per env; image built once |
| `FEATURE_AI_MATCH` | server → exposed at runtime | flag differs per env |

**No `NEXT_PUBLIC_` variables** because the image is promoted unchanged: build-time inlining would freeze staging values into production.

**Runtime exposure**: the root layout (Server Component) reads `ANALYTICS_ID` and `FEATURE_AI_MATCH` and passes them as props to a small client `ConfigProvider` (serializable values only), or a `GET /api/config` Route Handler returns the public subset. Browser data requests go through Route Handlers (BFF) that add the user's session and call `API_URL`.

**Validation** in `lib/env.ts` (server-only), run at startup/instrumentation: URLs must be http(s), token length ≥ 32 in production, flags must be `"true"`/`"false"`; errors list names only. `.env.example` documents all of them with placeholders.
:::

### 📝 Self-review checklist

- [ ] Secrets never reach the browser
- [ ] Build-once-deploy-many constraint handled
- [ ] Validation without leaking values

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/web/m4/w4/03-env-metadata" ai="no-ai" title="Validated env config and page metadata"}
Write a fail-fast server env reader and a browser-safe `publicEnv` with literal `NEXT_PUBLIC_` references, document variables in `.env.example`, and add root metadata with a title template plus `generateMetadata` for a dynamic job page (including a not-found variant with `noindex`).
:::

:::hints
- Collect problems in an array; throw once with only names in the message.
- `metadataBase: new URL("https://careerpilot.id")`.
- `generateMetadata` receives the same `params` Promise as the page.
:::

## ✅ Quick check

:::quiz
When is the value of `process.env.NEXT_PUBLIC_API_URL` decided for browser code?

At build time (`next build`) — it's replaced with a literal string in the JavaScript bundle.
:::

:::quiz
What does `title.template` in the root layout do?

It formats titles defined by child segments, e.g. `"%s · CareerPilot"` turns a page title "Jobs" into "Jobs · CareerPilot"; `title.default` is used when a child doesn't set a title.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Environment variable | Variabel lingkungan |
| Build time / runtime | Saat build / saat berjalan |
| Inlining | Menyisipkan nilai langsung ke kode |
| Metadata | Metadata — informasi tentang halaman |
| Open Graph | Protokol pratinjau tautan di media sosial |
| Canonical URL | URL utama/kanonik suatu halaman |

## 📚 Keep learning

- Next.js docs (bundled): Environment Variables guide; Metadata and OG images; `generateMetadata` reference
- [Open Graph protocol](https://ogp.me/)

# M4 · W6 · 05 — Deployment: standalone build, Docker, health check, CI

> 🤖✅ **AI-allowed** (explain every line you keep) · ⏱️ ~2 h

Make CareerPilot's Next.js frontend deployable **anywhere** (a VPS, AWS ECS/App Runner, Fly.io, Railway) — not only Vercel — with a small, secure Docker image, and a CI pipeline that blocks broken builds.

## 1. `next.config.ts`
`output: "standalone"` → `next build` creates `.next/standalone` with a minimal `server.js` and only the `node_modules` files it needs.

## 2. `lib/env.ts` — fail fast on bad configuration
`parseServerEnv(source: Record<string, string | undefined> = process.env)` with Zod:
- `API_URL`: URL · `SESSION_SECRET`: at least 32 characters · `NEXT_PUBLIC_APP_URL`: URL
- returns the typed object
- on failure throws `Error("Invalid environment variables: API_URL, SESSION_SECRET")` — names sorted, **never the values** (logs are not a safe place for secrets)

## 3. `app/api/health/route.ts`
`GET` → `200` JSON `{ status: "ok", version }` where `version = process.env.APP_VERSION ?? "dev"`, with header `Cache-Control: no-store`. Load balancers and Docker call this.

## 4. `Dockerfile` — three stages
| Stage | Must do |
|---|---|
| `deps` (`FROM node:24-alpine AS deps`) | `WORKDIR /app`, copy **only** `package.json package-lock.json`, `RUN npm ci` (layer cache survives code changes) |
| `builder` | copy `node_modules` from `deps`, `COPY . .`, `ENV NEXT_TELEMETRY_DISABLED=1`, `RUN npm run build` |
| `runner` | `ENV NODE_ENV=production PORT=3091 HOSTNAME=0.0.0.0` · copy `.next/standalone` → `./`, `.next/static` → `./.next/static`, `public` → `./public` (all `--chown=node:node`) · `USER node` · `EXPOSE 3091` · a `HEALTHCHECK` that requests `/api/health` · exec-form `CMD ["node", "server.js"]` |

Rules: pin the base image to a major version (no `latest`); no `npm` and no full `node_modules` in the runner; no secrets in `ARG`/`ENV` (they're baked into image layers).

## 5. `.dockerignore`
Exclude `node_modules`, `.next`, `.git`, `.env*` (but keep `!.env.example`), `playwright-report`, `test-results`.

## 6. `workflows/frontend.yml` (a GitHub Actions workflow)
- triggers: `push` to `main` and `pull_request`
- `permissions: contents: read`; `concurrency` with `cancel-in-progress: true`
- job **`quality`** (`ubuntu-latest`, `timeout-minutes`): checkout, setup-node (**pinned to full commit SHAs**, `node-version: 24`, `cache: npm`), `npm ci`, `npm run lint`, `npm run typecheck`, `npm test`
- job **`e2e`** (`needs: quality`, `timeout-minutes`): checkout + setup-node, `npm ci`, `npx playwright install --with-deps chromium`, `npm run build`, `npx playwright test`, then upload `playwright-report` with `actions/upload-artifact` (pinned SHA) **only when tests fail** (`if: failure()`), `retention-days: 7`

Pinned SHAs you can use: `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1`, `actions/setup-node@820762786026740c76f36085b0efc47a31fe5020 # v7.0.0`, `actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1`.

```bash
cd exercises/web
npx vitest run m4/w6/05-deployment
```
In a real project: `docker build -t careerpilot-web . && docker run --rm -p 3091:3091 --env-file .env.production careerpilot-web`.

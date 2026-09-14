# CareerPilot Phase 4 — starter kit (Next.js web app)

This kit contains the **acceptance tests** for your Next.js frontend and a **mock of the Phase 2 API**. You create the app itself.

```text
phase-4/
├── playwright.acceptance.config.ts   ← runs the mock API (5093) + a production build of your app (3091)
├── .env.example
└── e2e/
    ├── mock-api/server.mjs           ← in-memory API following the Phase 2 contract
    └── acceptance/                   ← 23 tests: auth, dashboard & navigation, companies, applications
```

## 1. Create the app
```bash
cd careerpilot                         # your monorepo from Phase 1–2
npx create-next-app@latest web --yes   # TypeScript, Tailwind, ESLint, App Router
cd web
npm install zod jose server-only
npm install -D @playwright/test
```
Set the dev port in `package.json`: `"dev": "next dev --port 3091"`.

## 2. Add the kit
Copy `playwright.acceptance.config.ts`, `.env.example` and the whole `e2e/` folder into `web/`. Add to `.gitignore`: `test-results/`, `playwright-report/`, `playwright/.auth/`.

```bash
npx playwright install --with-deps chromium    # or: PW_CHANNEL=chrome to use your installed Chrome
npx playwright test --config playwright.acceptance.config.ts                    # everything
npx playwright test --config playwright.acceptance.config.ts -g "registration"  # one checkpoint
npx playwright test --config playwright.acceptance.config.ts --ui               # debug
```
The config **builds your app** (`npm run build && npm run start`) and points it at the mock API through environment variables (`API_URL`, `SESSION_SECRET`, `NEXT_PUBLIC_APP_URL`, `COOKIE_SECURE=false`). While iterating, keep `npm run build && npm run start -- --port 3091` running yourself (the config reuses it) and set `FRESH_BUILD=1` when you want the config to rebuild.

## 3. Develop against your real API
```bash
# terminal 1 — Phase 2 API
cd ../api && docker compose up -d && uv run flask --app careerpilot_api run --port 5091
# terminal 2 — web
cp .env.example .env.local   # fill SESSION_SECRET
npm run dev
```
The mock only exists so the tests are fast and repeatable. **Both must work.**

## Rules
- Don't edit files in `e2e/acceptance/` or `e2e/mock-api/` — they are the contract. Write your own tests next to them.
- The UI contract (labels, headings, messages) is listed in the Phase 4 brief in the handbook.

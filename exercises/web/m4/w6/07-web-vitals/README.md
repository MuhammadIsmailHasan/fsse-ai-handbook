# M4 · W6 · 07 — Core Web Vitals: measure real users

> 🤖✅ **AI-allowed** · ⏱️ ~75 min · ⚪ optional

Lighthouse measures **your** laptop. Real users have slow phones and busy networks. Collect **field data** from CareerPilot users and summarize it the way Google does (the 75th percentile).

## 1. `lib/vitals.ts` (pure functions)
- `THRESHOLDS`: `LCP [2500, 4000]` ms · `INP [200, 500]` ms · `CLS [0.1, 0.25]` · `FCP [1800, 3000]` ms · `TTFB [800, 1800]` ms
- `rateMetric(name, value)` → `"good"` (≤ first), `"needs-improvement"` (≤ second), `"poor"`
- `formatMetric(name, value)` → CLS with 2 decimals (`"0.05"`), others rounded ms (`"2480 ms"`)
- `p75(values)` → nearest-rank 75th percentile: sort ascending, take index `ceil(0.75 × n) − 1`; empty → `null`
- `summarize(samples: { name, value }[])` → `{ [name]: { p75, rating, count } }` only for metrics present

## 2. `app/_components/web-vitals.tsx` (`"use client"`)
`WebVitals()` calls `useReportWebVitals(reportWebVital)` and renders nothing.
`reportWebVital(metric)` — defined **outside** the component so its reference is stable (otherwise metrics are reported twice):
- body: `JSON.stringify({ name, value, rating, id, navigationType, path: window.location.pathname })`
- if `navigator.sendBeacon` exists → `navigator.sendBeacon("/api/vitals", body)` (survives the page closing)
- otherwise → `fetch("/api/vitals", { method: "POST", body, keepalive: true, headers: { "Content-Type": "application/json" } })`

## 3. `app/api/vitals/route.ts`
`POST(request)`:
- `Content-Length` over **2048** bytes → `413`
- parse JSON and validate with Zod: `name` one of `LCP INP CLS FCP TTFB`, `value` ≥ 0, `rating` one of the three, `id` string ≤ 100, `navigationType` optional string, `path` string starting with `/` (≤ 200)
- invalid JSON or data → `400`
- valid → `console.info(JSON.stringify({ event: "web_vital", ...data }))` (one structured log line — ship it to your log tool) and `204`

```bash
cd exercises/web
npx vitest run m4/w6/07-web-vitals
```

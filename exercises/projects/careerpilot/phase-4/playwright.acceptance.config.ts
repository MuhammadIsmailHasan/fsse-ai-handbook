// CareerPilot Phase 4 — acceptance test configuration. Copy into your web/ folder unchanged.
//   npx playwright test --config playwright.acceptance.config.ts
import { defineConfig, devices } from "@playwright/test";

const WEB_PORT = Number(process.env.WEB_PORT ?? 3091);
const MOCK_API_PORT = Number(process.env.MOCK_API_PORT ?? 5093);
const CI = !!process.env.CI;

export default defineConfig({
  testDir: "./e2e/acceptance",
  fullyParallel: true,
  forbidOnly: CI,
  retries: CI ? 1 : 0,
  workers: CI ? 2 : undefined,
  reporter: CI ? [["github"], ["html", { open: "never" }]] : [["list"], ["html", { open: "never" }]],
  timeout: 30_000,
  use: {
    baseURL: `http://localhost:${WEB_PORT}`,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    channel: process.env.PW_CHANNEL,
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"], channel: process.env.PW_CHANNEL } }],
  webServer: [
    {
      command: "node e2e/mock-api/server.mjs",
      url: `http://localhost:${MOCK_API_PORT}/health/live`,
      env: { MOCK_API_PORT: String(MOCK_API_PORT) },
      reuseExistingServer: false,
    },
    {
      // A production build: the same code you deploy.
      command: `npm run build && npm run start -- --port ${WEB_PORT}`,
      url: `http://localhost:${WEB_PORT}/login`,
      timeout: 240_000,
      reuseExistingServer: !CI && !process.env.FRESH_BUILD,
      env: {
        API_URL: `http://localhost:${MOCK_API_PORT}`,
        SESSION_SECRET: "acceptance-tests-only-secret-0123456789abcdef",
        NEXT_PUBLIC_APP_URL: `http://localhost:${WEB_PORT}`,
        COOKIE_SECURE: "false", // the tests use http://localhost
      },
    },
  ],
});

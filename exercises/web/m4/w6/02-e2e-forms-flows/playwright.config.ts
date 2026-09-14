// Provided. You'll write a config like this yourself in exercise 01.
import { existsSync } from "node:fs";
import { chromium, defineConfig, devices } from "@playwright/test";

const PORT = Number(process.env.PORT ?? 3191);

// Use Playwright's Chromium if installed (`npx playwright install chromium`), otherwise your Google Chrome.
const channel = process.env.PW_CHANNEL ?? (existsSync(chromium.executablePath()) ? undefined : "chrome");

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: "list",
  use: {
    baseURL: `http://localhost:${PORT}`,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"], channel } }],
  webServer: {
    command: "node ../_app/server.mjs",
    url: `http://localhost:${PORT}/health`,
    reuseExistingServer: !process.env.CI && !process.env.APP_VARIANT,
    env: { PORT: String(PORT), APP_VARIANT: process.env.APP_VARIANT ?? "" },
  },
});

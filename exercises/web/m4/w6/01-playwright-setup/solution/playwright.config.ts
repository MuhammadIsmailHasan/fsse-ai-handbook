import { existsSync } from "node:fs";
import { chromium, defineConfig, devices } from "@playwright/test";

const PORT = Number(process.env.PORT ?? 3191);
const CI = !!process.env.CI;

// Playwright's Chromium if installed, otherwise the local Google Chrome.
const channel = process.env.PW_CHANNEL ?? (existsSync(chromium.executablePath()) ? undefined : "chrome");

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: CI,
  retries: CI ? 2 : 0,
  workers: CI ? 1 : undefined,
  reporter: CI ? [["github"], ["html", { open: "never" }]] : [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: `http://localhost:${PORT}`,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"], channel } },
    { name: "mobile", use: { ...devices["Pixel 7"], channel } },
  ],
  webServer: {
    command: "node ../_app/server.mjs",
    url: `http://localhost:${PORT}/health`,
    reuseExistingServer: !CI,
    timeout: 30_000,
    env: { PORT: String(PORT) },
  },
});

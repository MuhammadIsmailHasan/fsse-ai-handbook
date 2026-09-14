// Provided: a "setup" project logs in once and saves the session; the other tests reuse it.
import { existsSync } from "node:fs";
import { chromium, defineConfig, devices } from "@playwright/test";

const PORT = Number(process.env.PORT ?? 3191);
const channel = process.env.PW_CHANNEL ?? (existsSync(chromium.executablePath()) ? undefined : "chrome");
export const AUTH_FILE = "playwright/.auth/user.json"; // gitignored — contains a session cookie

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: "list",
  use: { baseURL: `http://localhost:${PORT}`, trace: "on-first-retry" },
  projects: [
    { name: "setup", testMatch: /.*\.setup\.ts/, use: { channel } },
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"], channel, storageState: AUTH_FILE },
      dependencies: ["setup"],
    },
  ],
  webServer: {
    command: "node ../_app/server.mjs",
    url: `http://localhost:${PORT}/health`,
    reuseExistingServer: !process.env.CI && !process.env.APP_VARIANT,
    env: { PORT: String(PORT), APP_VARIANT: process.env.APP_VARIANT ?? "" },
  },
});

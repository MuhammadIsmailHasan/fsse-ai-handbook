// @vitest-environment node
import { afterEach, describe, expect, test, vi } from "vitest";
import { runPlaywright } from "@support/playwright";
import { typecheckFolder } from "@support/typecheck";

type Config = Awaited<typeof import("./playwright.config")>["default"];

async function loadConfig(env: Record<string, string | undefined>): Promise<Config> {
  vi.resetModules();
  for (const [key, value] of Object.entries(env)) vi.stubEnv(key, value);
  return (await import("./playwright.config")).default;
}

afterEach(() => vi.unstubAllEnvs());

describe("playwright.config.ts", () => {
  test("local settings", async () => {
    const config = await loadConfig({ CI: "", PORT: undefined });
    expect(config.testDir).toBe("./e2e");
    expect(config.fullyParallel).toBe(true);
    expect(config.forbidOnly).toBe(false);
    expect(config.retries).toBe(0);
    expect(config.workers).toBeUndefined();
    expect(config.reporter).toEqual([["list"], ["html", { open: "never" }]]);
    expect(config.use).toMatchObject({ baseURL: "http://localhost:3191", trace: "on-first-retry", screenshot: "only-on-failure" });
    const server = Array.isArray(config.webServer) ? config.webServer[0] : config.webServer;
    expect(server).toMatchObject({ command: "node ../_app/server.mjs", url: "http://localhost:3191/health", reuseExistingServer: true, timeout: 30_000, env: { PORT: "3191" } });
  });

  test("CI settings and PORT", async () => {
    const config = await loadConfig({ CI: "true", PORT: "4555" });
    expect(config.forbidOnly).toBe(true);
    expect(config.retries).toBe(2);
    expect(config.workers).toBe(1);
    expect(config.reporter).toEqual([["github"], ["html", { open: "never" }]]);
    expect(config.use?.baseURL).toBe("http://localhost:4555");
    const server = Array.isArray(config.webServer) ? config.webServer[0] : config.webServer;
    expect(server?.reuseExistingServer).toBe(false);
  });

  test("projects", async () => {
    const config = await loadConfig({ CI: "" });
    expect(config.projects?.map((p) => p.name)).toEqual(["chromium", "mobile"]);
    const [desktop, mobile] = config.projects!;
    expect(desktop!.use).toMatchObject({ viewport: { width: 1280, height: 720 } });
    expect(mobile!.use).toMatchObject({ isMobile: true, hasTouch: true });
    for (const project of config.projects!) expect(project.use).toHaveProperty("channel");
  });
});

test("smoke tests pass in both projects", { timeout: 180_000 }, async () => {
  const run = await runPlaywright(import.meta.dirname);
  expect(run.unexpected, run.output).toBe(0);
  expect(run.expected, "2 tests × 2 projects").toBeGreaterThanOrEqual(4);
});

test("types", () => {
  expect(typecheckFolder(import.meta.dirname, { recursive: true }).output).toBe("");
});

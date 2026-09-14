/** Test helpers for the Playwright (E2E) exercises. */
import { spawnSync } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { createServer } from "node:net";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { chromium } from "@playwright/test";

/**
 * Browser to use: Playwright's own Chromium when installed (`npx playwright install chromium`),
 * otherwise your installed Google Chrome (`channel: "chrome"`).
 */
export function browserChannel(): string | undefined {
  if (process.env.PW_CHANNEL) return process.env.PW_CHANNEL;
  try {
    return existsSync(chromium.executablePath()) ? undefined : "chrome";
  } catch {
    return "chrome";
  }
}

export function findWebRoot(start: string): string {
  let dir = start;
  while (!existsSync(join(dir, "vitest.config.ts"))) {
    const parent = dirname(dir);
    if (parent === dir) throw new Error("exercises/web root not found");
    dir = parent;
  }
  return dir;
}

export async function freePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const server = createServer();
    server.listen(0, () => {
      const address = server.address();
      server.close(() => (typeof address === "object" && address ? resolve(address.port) : reject(new Error("no port"))));
    });
  });
}

export type PlaywrightRun = { exitCode: number; expected: number; unexpected: number; skipped: number; output: string };

/** Runs `playwright test` for one exercise folder against the mini app, optionally with one bug switched on. */
export async function runPlaywright(exerciseDir: string, options: { variant?: string } = {}): Promise<PlaywrightRun> {
  const webRoot = findWebRoot(exerciseDir);
  const reportDir = mkdtempSync(join(tmpdir(), "pw-report-"));
  const reportFile = join(reportDir, "report.json");
  const port = await freePort();
  const result = spawnSync(join(webRoot, "node_modules", ".bin", "playwright"), ["test", "--config", join(exerciseDir, "playwright.config.ts"), "--reporter", "json"], {
    cwd: exerciseDir,
    encoding: "utf8",
    env: { ...process.env, PORT: String(port), APP_VARIANT: options.variant ?? "", PLAYWRIGHT_JSON_OUTPUT_NAME: reportFile, CI: "", FORCE_COLOR: "0" },
    timeout: 240_000,
  });
  try {
    const report = existsSync(reportFile) ? JSON.parse(readFileSync(reportFile, "utf8")) : null;
    const stats = report?.stats ?? {};
    const errors = (report?.errors ?? []).map((e: { message?: string }) => e.message ?? "").join("\n");
    return {
      exitCode: result.status ?? 1,
      expected: stats.expected ?? 0,
      unexpected: stats.unexpected ?? 0,
      skipped: stats.skipped ?? 0,
      output: `${errors}\n${result.stdout ?? ""}\n${result.stderr ?? ""}`.slice(-3000),
    };
  } finally {
    rmSync(reportDir, { recursive: true, force: true });
  }
}

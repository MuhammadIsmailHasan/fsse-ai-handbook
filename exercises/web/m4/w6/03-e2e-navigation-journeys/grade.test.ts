// @vitest-environment node
// Grades YOUR Playwright tests — you don't need to edit this file.
import { readFileSync } from "node:fs";
import { describe, expect, test } from "vitest";
import { runPlaywright } from "@support/playwright";
import { typecheckFolder } from "@support/typecheck";

const MUTANTS = [
  "no-auth-guard",
  "nav-no-aria-current",
  "search-case-sensitive",
  "pagination-stuck",
  "missing-application-200",
  "logout-keeps-session",
  "breadcrumb-wrong-link",
  "detail-generic-title",
];

describe("your E2E tests", { timeout: 300_000 }, () => {
  test("pass against the correct app (setup + at least 8 tests)", async () => {
    const run = await runPlaywright(import.meta.dirname);
    expect(run.unexpected, run.output).toBe(0);
    expect(run.expected, "setup + 8 tests").toBeGreaterThanOrEqual(9);
  });

  test.concurrent.each(MUTANTS)("catch the bug: %s", async (variant) => {
    const run = await runPlaywright(import.meta.dirname, { variant });
    expect(run.expected + run.unexpected, run.output).toBeGreaterThan(0);
    expect(run.unexpected, `Bug "${variant}" SURVIVED — none of your tests noticed it.`).toBeGreaterThan(0);
  });

  test("reuses a saved session and uses test.step", () => {
    const setup = readFileSync(`${import.meta.dirname}/e2e/auth.setup.ts`, "utf8");
    expect(setup).toMatch(/storageState\(\s*\{\s*path/);
    expect(readFileSync(`${import.meta.dirname}/e2e/journeys.spec.ts`, "utf8")).toMatch(/test\.step\(/);
    expect(typecheckFolder(import.meta.dirname, { recursive: true }).output).toBe("");
  });
});

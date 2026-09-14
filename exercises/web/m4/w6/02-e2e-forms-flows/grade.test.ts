// @vitest-environment node
// Grades YOUR Playwright tests — you don't need to edit this file.
import { describe, expect, test } from "vitest";
import { runPlaywright } from "@support/playwright";
import { typecheckFolder } from "@support/typecheck";

const MUTANTS = [
  "login-error-hidden",
  "login-ignores-next",
  "role-not-required",
  "salary-range-unchecked",
  "errors-clear-values",
  "no-created-flash",
  "created-not-listed",
  "status-not-saved",
  "cancel-deletes",
];

describe("your E2E tests", { timeout: 300_000 }, () => {
  test("pass against the correct app (at least 7 tests)", async () => {
    const run = await runPlaywright(import.meta.dirname);
    expect(run.unexpected, run.output).toBe(0);
    expect(run.expected, "Write at least 7 tests").toBeGreaterThanOrEqual(7);
  });

  test.concurrent.each(MUTANTS)("catch the bug: %s", async (variant) => {
    const run = await runPlaywright(import.meta.dirname, { variant });
    expect(run.expected + run.unexpected, run.output).toBeGreaterThan(0);
    expect(run.unexpected, `Bug "${variant}" SURVIVED — none of your tests noticed it.`).toBeGreaterThan(0);
  });

  test("use page objects with accessible locators", () => {
    expect(typecheckFolder(import.meta.dirname, { recursive: true }).output).toBe("");
  });
});

// @vitest-environment node
// Grades YOUR tests (applications-table.test.tsx) — you don't need to edit this file.
import { readdirSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, test } from "vitest";
import { runLearnerTests } from "@support/mutation";

const dir = import.meta.dirname;
const MUTANTS = readdirSync(join(dir, "mutants")).filter((f) => f.endsWith(".tsx")).sort();
const run = (implementation: string) =>
  runLearnerTests(dir, { target: "applications-table.tsx", implementation, testFiles: ["applications-table.test.tsx"] });

describe("your component tests", { timeout: 120_000 }, () => {
  test("pass against the real component (at least 5 tests)", () => {
    const result = run(join(dir, "applications-table.tsx"));
    expect(result.loadErrors, result.output).toBe(0);
    expect(result.failed, result.output).toBe(0);
    expect(result.passed, "Write at least 5 tests").toBeGreaterThanOrEqual(5);
  });

  test.concurrent.each(MUTANTS)("catch the bug: %s", async (mutant) => {
    const result = run(join(dir, "mutants", mutant));
    expect(result.loadErrors, `Your test file crashed instead of failing:\n${result.output}`).toBe(0);
    expect(result.failed, `Mutant ${mutant} SURVIVED — no test noticed this bug.`).toBeGreaterThan(0);
  });
});

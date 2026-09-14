/** Test helper: run a learner's Vitest tests against an implementation file (the real one or a mutant). */
import { spawnSync } from "node:child_process";
import { cpSync, existsSync, mkdirSync, readFileSync, rmSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { randomUUID } from "node:crypto";

function findWebRoot(start: string): string {
  let dir = start;
  while (!existsSync(join(dir, "vitest.config.ts"))) {
    const parent = dirname(dir);
    if (parent === dir) throw new Error("exercises/web root not found");
    dir = parent;
  }
  return dir;
}

export type VitestRun = { passed: number; failed: number; loadErrors: number; output: string };

/**
 * Copies the exercise (without solution/, mutants/ and the grader) to a temp folder, replaces `target`
 * with `implementation`, and runs only the learner's test files there.
 */
export function runLearnerTests(exerciseDir: string, options: { target: string; implementation: string; testFiles: string[] }): VitestRun {
  const webRoot = findWebRoot(exerciseDir);
  const tmp = join(webRoot, ".grader-tmp", randomUUID());
  mkdirSync(tmp, { recursive: true });
  const report = join(tmp, "report.json");
  try {
    for (const file of options.testFiles) cpSync(join(exerciseDir, file), join(tmp, file));
    cpSync(options.implementation, join(tmp, options.target));
    const result = spawnSync(
      join(webRoot, "node_modules", ".bin", "vitest"),
      ["run", relative(webRoot, tmp), "--reporter=json", `--outputFile=${report}`],
      { cwd: webRoot, encoding: "utf8", timeout: 120_000, env: { ...process.env, VITEST: undefined, VITEST_POOL_ID: undefined, VITEST_WORKER_ID: undefined, FORCE_COLOR: "0" } },
    );
    if (!existsSync(report)) return { passed: 0, failed: 0, loadErrors: 1, output: `${result.stdout}\n${result.stderr}`.slice(-3000) };
    const json = JSON.parse(readFileSync(report, "utf8"));
    const loadErrors = (json.testResults ?? []).filter((file: { assertionResults: unknown[]; status: string }) => file.status === "failed" && file.assertionResults.length === 0).length;
    const messages = (json.testResults ?? [])
      .flatMap((file: { message?: string; assertionResults: { status: string; fullName: string; failureMessages: string[] }[] }) => [
        file.message ?? "",
        ...file.assertionResults.filter((a) => a.status === "failed").map((a) => `✗ ${a.fullName}\n${a.failureMessages.join("\n").slice(0, 600)}`),
      ])
      .filter(Boolean)
      .join("\n");
    return { passed: json.numPassedTests ?? 0, failed: json.numFailedTests ?? 0, loadErrors, output: messages.slice(-3000) };
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
}

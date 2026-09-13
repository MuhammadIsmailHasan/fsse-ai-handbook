/** Test helper: type-check one exercise folder with the TypeScript compiler (tsc). */
import { execFileSync } from "node:child_process";
import { existsSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";

function webRoot(start: string): string {
  let dir = start;
  while (!existsSync(join(dir, "vitest.config.ts"))) {
    const parent = dirname(dir);
    if (parent === dir) throw new Error("exercises/web root not found");
    dir = parent;
  }
  return dir;
}

export type TypecheckResult = { ok: boolean; output: string };

/** Type-checks .ts/.tsx files directly inside `dir` (or all subfolders with `recursive`), never tests or solution/. */
export function typecheckFolder(dir: string, options: { recursive?: boolean } = {}): TypecheckResult {
  const root = webRoot(dir);
  const files = options.recursive
    ? ["**/*.ts", "**/*.tsx"]
    : readdirSync(dir).filter((f) => /\.(ts|tsx)$/.test(f) && !f.endsWith(".test.ts") && !f.endsWith(".test.tsx"));
  const exclude = options.recursive ? ["**/*.test.ts", "**/*.test.tsx", "solution/**"] : [];
  const config = join(dir, "tsconfig.check.json");
  writeFileSync(
    config,
    JSON.stringify({ extends: relative(dir, join(root, "tsconfig.json")), compilerOptions: { noEmit: true }, include: files, exclude }),
  );
  try {
    execFileSync(join(root, "node_modules", ".bin", "tsc"), ["-p", config, "--pretty", "false"], { encoding: "utf8", stdio: "pipe" });
    return { ok: true, output: "" };
  } catch (error) {
    const e = error as { stdout?: string; stderr?: string };
    return { ok: false, output: `${e.stdout ?? ""}${e.stderr ?? ""}`.replaceAll(dir + "/", "") };
  } finally {
    rmSync(config, { force: true });
  }
}

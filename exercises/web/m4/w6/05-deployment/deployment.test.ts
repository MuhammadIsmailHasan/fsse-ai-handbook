// @vitest-environment node
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { parse } from "yaml";
import { afterEach, describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import nextConfig from "./next.config";
import { GET } from "./app/api/health/route";
import { parseServerEnv } from "./lib/env";

const dir = import.meta.dirname;
const read = (file: string) => readFileSync(join(dir, file), "utf8");

afterEach(() => vi.unstubAllEnvs());

type Instruction = { op: string; args: string };
type Stage = { name: string; image: string; steps: Instruction[] };

function parseDockerfile(source: string): Stage[] {
  const lines = source
    .replace(/\\\r?\n/g, " ")
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter((l) => l && !l.startsWith("#"));
  const stages: Stage[] = [];
  for (const line of lines) {
    const [, op = "", args = ""] = line.match(/^(\w+)\s+(.*)$/) ?? [];
    if (op.toUpperCase() === "FROM") {
      const [, image = "", name = ""] = args.match(/^(\S+)(?:\s+AS\s+(\S+))?/i) ?? [];
      stages.push({ name: name.toLowerCase(), image, steps: [] });
    } else stages.at(-1)?.steps.push({ op: op.toUpperCase(), args: args.replace(/\s+/g, " ") });
  }
  return stages;
}

describe("next.config.ts", () => {
  test("standalone output", () => {
    expect(nextConfig.output).toBe("standalone");
  });
});

describe("environment validation", () => {
  const valid = { API_URL: "http://api:5091", SESSION_SECRET: "x".repeat(32), NEXT_PUBLIC_APP_URL: "https://careerpilot.app" };

  test("returns typed values", () => {
    expect(parseServerEnv({ ...valid, OTHER: "ignored" })).toEqual(valid);
  });

  test("names the broken variables, never their values", () => {
    const secret = "too-short-secret-value";
    let message = "";
    try {
      parseServerEnv({ ...valid, SESSION_SECRET: secret, API_URL: "not a url", NEXT_PUBLIC_APP_URL: undefined });
    } catch (error) {
      message = (error as Error).message;
    }
    expect(message).toBe("Invalid environment variables: API_URL, NEXT_PUBLIC_APP_URL, SESSION_SECRET");
    expect(message).not.toContain(secret);
    expect(message).not.toContain("not a url");
  });

  test("defaults to process.env", () => {
    for (const [k, v] of Object.entries(valid)) vi.stubEnv(k, v);
    expect(parseServerEnv().API_URL).toBe("http://api:5091");
  });
});

describe("health check", () => {
  test("ok with version and no caching", async () => {
    vi.stubEnv("APP_VERSION", "2026.09.1");
    vi.stubEnv("SESSION_SECRET", "super-secret-value-that-must-not-leak");
    const response = await GET();
    expect(response.status).toBe(200);
    expect(response.headers.get("cache-control")).toBe("no-store");
    const text = await response.text();
    expect(JSON.parse(text)).toEqual({ status: "ok", version: "2026.09.1" });
    expect(text).not.toContain("super-secret");
    vi.stubEnv("APP_VERSION", undefined);
    expect(await (await GET()).json()).toEqual({ status: "ok", version: "dev" });
  });
});

describe("Dockerfile", () => {
  const stages = () => parseDockerfile(read("Dockerfile"));
  const stage = (name: string) => {
    const found = stages().find((s) => s.name === name);
    expect(found, `stage "${name}"`).toBeDefined();
    return found!;
  };
  const has = (s: Stage, op: string, pattern: RegExp) => s.steps.some((step) => step.op === op && pattern.test(step.args));

  test("three stages on a pinned Node 24 image", () => {
    expect(stages().map((s) => s.name)).toEqual(["deps", "builder", "runner"]);
    for (const s of stages()) expect(s.image).toMatch(/^node:24(\.\d+)*-alpine(@sha256:[a-f0-9]{64})?$/);
  });

  test("deps stage caches npm ci", () => {
    const deps = stage("deps");
    const copyIndex = deps.steps.findIndex((s) => s.op === "COPY" && /^package\.json package-lock\.json \.\/?$/.test(s.args));
    const ciIndex = deps.steps.findIndex((s) => s.op === "RUN" && /^npm ci\b/.test(s.args));
    expect(copyIndex).toBeGreaterThanOrEqual(0);
    expect(ciIndex).toBeGreaterThan(copyIndex);
    expect(deps.steps.some((s) => s.op === "COPY" && /^\. /.test(s.args))).toBe(false);
  });

  test("builder stage", () => {
    const builder = stage("builder");
    expect(has(builder, "COPY", /--from=deps \/app\/node_modules \.\/node_modules/)).toBe(true);
    expect(has(builder, "COPY", /^\. \.$/)).toBe(true);
    expect(has(builder, "ENV", /NEXT_TELEMETRY_DISABLED=1/)).toBe(true);
    expect(has(builder, "RUN", /^npm run build$/)).toBe(true);
  });

  test("runner stage is minimal and non-root", () => {
    const runner = stage("runner");
    const env = runner.steps.filter((s) => s.op === "ENV").map((s) => s.args).join(" ");
    expect(env).toMatch(/NODE_ENV=production/);
    expect(env).toMatch(/PORT=3091/);
    expect(env).toMatch(/HOSTNAME=0\.0\.0\.0/);
    expect(has(runner, "COPY", /--from=builder --chown=node:node \/app\/\.next\/standalone \.\/?$/)).toBe(true);
    expect(has(runner, "COPY", /--from=builder --chown=node:node \/app\/\.next\/static \.\/\.next\/static$/)).toBe(true);
    expect(has(runner, "COPY", /--from=builder --chown=node:node \/app\/public \.\/public$/)).toBe(true);
    const userIndex = runner.steps.findIndex((s) => s.op === "USER" && s.args === "node");
    const cmdIndex = runner.steps.findIndex((s) => s.op === "CMD");
    expect(userIndex).toBeGreaterThanOrEqual(0);
    expect(cmdIndex).toBeGreaterThan(userIndex);
    expect(has(runner, "EXPOSE", /^3091$/)).toBe(true);
    expect(has(runner, "HEALTHCHECK", /\/api\/health/)).toBe(true);
    expect(runner.steps[cmdIndex]!.args).toMatch(/^\[\s*"node",\s*"server\.js"\s*\]$/);
    expect(runner.steps.some((s) => s.op === "RUN" && /\bnpm\b/.test(s.args))).toBe(false);
    expect(runner.steps.some((s) => s.op === "COPY" && /node_modules/.test(s.args))).toBe(false);
  });

  test("no secrets baked into the image", () => {
    for (const s of stages()) {
      for (const step of s.steps.filter((x) => x.op === "ARG" || x.op === "ENV")) {
        expect(step.args).not.toMatch(/SECRET|TOKEN|PASSWORD|API_KEY/i);
      }
    }
  });
});

test(".dockerignore", () => {
  const entries = read(".dockerignore").split(/\r?\n/).map((l) => l.trim()).filter((l) => l && !l.startsWith("#"));
  for (const required of ["node_modules", ".next", ".git", ".env*", "!.env.example", "playwright-report", "test-results"]) {
    expect(entries).toContain(required);
  }
  expect(entries.indexOf("!.env.example")).toBeGreaterThan(entries.indexOf(".env*"));
});

describe("workflows/frontend.yml", () => {
  const workflow = () => parse(read("workflows/frontend.yml"));
  const SHA = /^[\w.-]+\/[\w.-]+@[0-9a-f]{40}$/;
  type Step = { uses?: string; run?: string; with?: Record<string, unknown>; if?: string };

  test("triggers, permissions, concurrency", () => {
    const wf = workflow();
    expect(wf.on.push.branches).toEqual(["main"]);
    expect(wf.on).toHaveProperty("pull_request");
    expect(wf.permissions).toEqual({ contents: "read" });
    expect(wf.concurrency["cancel-in-progress"]).toBe(true);
    expect(String(wf.concurrency.group)).toContain("${{ github.ref }}");
  });

  test("quality job", () => {
    const job = workflow().jobs.quality;
    expect(job["runs-on"]).toBe("ubuntu-latest");
    expect(job["timeout-minutes"]).toBeGreaterThan(0);
    const steps: Step[] = job.steps;
    const uses = steps.filter((s) => s.uses).map((s) => s.uses!);
    expect(uses.map((u) => u.split("@")[0])).toEqual(["actions/checkout", "actions/setup-node"]);
    for (const u of uses) expect(u).toMatch(SHA);
    const node = steps.find((s) => s.uses?.startsWith("actions/setup-node"))!;
    expect(node.with).toMatchObject({ "node-version": 24, cache: "npm" });
    expect(steps.filter((s) => s.run).map((s) => s.run!.trim())).toEqual(["npm ci", "npm run lint", "npm run typecheck", "npm test"]);
  });

  test("e2e job", () => {
    const job = workflow().jobs.e2e;
    expect(job.needs).toBe("quality");
    expect(job["timeout-minutes"]).toBeGreaterThan(0);
    const steps: Step[] = job.steps;
    const runs = steps.filter((s) => s.run).map((s) => s.run!.trim());
    expect(runs).toEqual(["npm ci", "npx playwright install --with-deps chromium", "npm run build", "npx playwright test"]);
    const upload = steps.at(-1)!;
    expect(upload.uses).toMatch(/^actions\/upload-artifact@[0-9a-f]{40}$/);
    expect(upload.if).toBe("failure()");
    expect(upload.with).toMatchObject({ path: "playwright-report", "retention-days": 7 });
    for (const s of steps.filter((x) => x.uses)) expect(s.uses).toMatch(SHA);
  });
});

test("types", () => {
  expect(typecheckFolder(dir, { recursive: true }).output).toBe("");
});

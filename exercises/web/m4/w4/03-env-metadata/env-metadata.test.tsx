import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";

vi.mock("next/navigation", () => ({ notFound: () => { throw new Error("NEXT_NOT_FOUND"); } }));

const here = (...p: string[]) => join(import.meta.dirname, ...p);
const GOOD = { API_URL: "https://api.careerpilot.id/", API_TOKEN: "t".repeat(32), APP_ENV: "production" };

afterEach(() => {
  vi.unstubAllEnvs();
  vi.resetModules();
});

describe("readServerEnv", () => {
  test("parses and normalizes", async () => {
    const { readServerEnv } = await import("./lib/env");
    expect(readServerEnv(GOOD)).toEqual({ apiUrl: "https://api.careerpilot.id", apiToken: "t".repeat(32), appEnv: "production" });
    expect(readServerEnv({ ...GOOD, APP_ENV: undefined }).appEnv).toBe("development");
  });

  test("reports every problem without leaking values", async () => {
    const { readServerEnv } = await import("./lib/env");
    let message = "";
    try {
      readServerEnv({ API_URL: "localhost:5091", API_TOKEN: "short-secret-123", APP_ENV: "staging" });
    } catch (error) {
      message = (error as Error).message;
    }
    for (const name of ["API_URL", "API_TOKEN", "APP_ENV"]) expect(message).toContain(name);
    expect(message).not.toContain("short-secret-123");
    expect(message).not.toContain("staging");
  });
});

describe("publicEnv", () => {
  test("defaults and values from NEXT_PUBLIC_ variables", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "");
    vi.resetModules();
    delete process.env.NEXT_PUBLIC_API_URL;
    delete process.env.NEXT_PUBLIC_APP_NAME;
    expect((await import("./lib/env")).publicEnv).toEqual({ apiUrl: "http://localhost:5091", appName: "CareerPilot" });
    vi.resetModules();
    vi.stubEnv("NEXT_PUBLIC_API_URL", "https://api.careerpilot.id");
    vi.stubEnv("NEXT_PUBLIC_APP_NAME", "CareerPilot Staging");
    expect((await import("./lib/env")).publicEnv).toEqual({ apiUrl: "https://api.careerpilot.id", appName: "CareerPilot Staging" });
  });

  test("uses literal process.env references only", () => {
    const source = readFileSync(here("lib/env.ts"), "utf8");
    expect(source).toContain("process.env.NEXT_PUBLIC_API_URL");
    expect(source).toContain("process.env.NEXT_PUBLIC_APP_NAME");
    expect(source).not.toMatch(/process\.env\[/);
  });
});

test(".env.example documents variables with placeholders", () => {
  const file = here(".env.example");
  expect(existsSync(file)).toBe(true);
  const entries = Object.fromEntries(
    readFileSync(file, "utf8")
      .split("\n")
      .filter((line) => /^[A-Z_]+=/.test(line))
      .map((line) => line.split(/=(.*)/s).slice(0, 2)),
  );
  for (const key of ["API_URL", "API_TOKEN", "APP_ENV", "NEXT_PUBLIC_API_URL", "NEXT_PUBLIC_APP_NAME"]) expect(entries, key).toHaveProperty(key);
  expect(entries.API_TOKEN).toMatch(/^(change-me|changeme|your-.*|<.*>|)$/);
});

describe("metadata", () => {
  test("root layout metadata and markup", async () => {
    const { metadata, default: RootLayout } = await import("./app/layout");
    expect(metadata.metadataBase?.toString()).toBe("https://careerpilot.id/");
    expect(metadata.title).toEqual({ default: "CareerPilot", template: "%s · CareerPilot" });
    expect(String(metadata.description).length).toBeGreaterThan(10);
    expect(metadata.openGraph).toMatchObject({ siteName: "CareerPilot", locale: "id_ID", type: "website" });
    expect(renderToStaticMarkup(<RootLayout><p>x</p></RootLayout>)).toMatch(/^<html lang="en">(<head><\/head>)?<body><p>x<\/p><\/body><\/html>$/);
  });

  test("generateMetadata for a job and for a missing job", async () => {
    const page = await import("./app/jobs/[id]/page");
    await expect(page.generateMetadata({ params: Promise.resolve({ id: "1" }) })).resolves.toEqual({
      title: "Backend Engineer",
      description: "Backend Engineer at Kopi Data in Jakarta",
      alternates: { canonical: "/jobs/1" },
      openGraph: { title: "Backend Engineer", description: "Backend Engineer at Kopi Data in Jakarta", url: "/jobs/1" },
    });
    await expect(page.generateMetadata({ params: Promise.resolve({ id: "9" }) })).resolves.toEqual({ title: "Job not found", robots: { index: false } });
    expect(renderToStaticMarkup(await page.default({ params: Promise.resolve({ id: "1" }) }))).toBe("<h1>Backend Engineer</h1>");
  });
});

test("types", () => {
  expect(typecheckFolder(import.meta.dirname, { recursive: true }).output).toBe("");
});

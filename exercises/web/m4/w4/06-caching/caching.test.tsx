import { render, screen } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { isValidElement, Suspense, type ReactElement } from "react";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";

const cache = vi.hoisted(() => ({ cacheLife: vi.fn(), cacheTag: vi.fn(), updateTag: vi.fn(), cookie: undefined as string | undefined }));
vi.mock("next/cache", () => ({ cacheLife: cache.cacheLife, cacheTag: cache.cacheTag, updateTag: cache.updateTag, revalidateTag: vi.fn() }));
vi.mock("next/headers", () => ({
  cookies: async () => ({ get: (name: string) => (name === "session" && cache.cookie ? { name, value: cache.cookie } : undefined) }),
}));

const source = (p: string) => readFileSync(join(import.meta.dirname, p), "utf8");
const json = (status: number, body: unknown) => new Response(JSON.stringify(body), { status });

beforeEach(() => {
  vi.stubEnv("API_URL", "http://flask:5091");
  Object.values(cache).forEach((v) => typeof v === "function" && (v as ReturnType<typeof vi.fn>).mockReset());
  cache.cookie = undefined;
});
afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

test("Cache Components is enabled", async () => {
  expect((await import("./next.config")).default).toEqual({ cacheComponents: true });
});

describe("cached public data", () => {
  test('directives come first in each cached function', () => {
    const jobs = source("lib/jobs.ts");
    const bodies = [...jobs.matchAll(/export async function (\w+)\([^)]*\)[^{]*{\s*([^\n]+)/g)].map((m) => [m[1], m[2]!.trim()]);
    expect(bodies).toEqual([
      ["getPublicJobs", expect.stringMatching(/^["']use cache["'];?$/)],
      ["getJob", expect.stringMatching(/^["']use cache["'];?$/)],
    ]);
  });

  test("getPublicJobs sets lifetime and tag, fetches without auth", async () => {
    const fetchMock = vi.fn(async () => json(200, { data: [{ id: 1, title: "Backend Engineer", company: "Kopi Data" }] }));
    vi.stubGlobal("fetch", fetchMock);
    const { getPublicJobs } = await import("./lib/jobs");
    await expect(getPublicJobs()).resolves.toEqual([{ id: 1, title: "Backend Engineer", company: "Kopi Data" }]);
    expect(cache.cacheLife).toHaveBeenCalledWith("hours");
    expect(cache.cacheTag).toHaveBeenCalledWith("jobs");
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit | undefined];
    expect(url).toBe("http://flask:5091/api/v1/jobs");
    expect(JSON.stringify(init ?? {})).not.toContain("Authorization");
  });

  test("getJob uses a per-job tag", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json(200, { data: { id: 7, title: "QA", company: "Batik" } })));
    const { getJob } = await import("./lib/jobs");
    await expect(getJob(7)).resolves.toMatchObject({ id: 7 });
    expect(cache.cacheTag).toHaveBeenCalledWith("jobs", "job-7");
    expect(cache.cacheLife).toHaveBeenCalledWith("hours");
  });

  test("personal data is never cached", async () => {
    expect(source("lib/applications.ts")).not.toMatch(/["']use cache/);
    const fetchMock = vi.fn(async () => json(200, { data: [{ id: 1, role: "Dev" }] }));
    vi.stubGlobal("fetch", fetchMock);
    const { getMyApplications } = await import("./lib/applications");
    await expect(getMyApplications("tok")).resolves.toHaveLength(1);
    expect(fetchMock).toHaveBeenCalledWith("http://flask:5091/api/v1/applications", { headers: { Authorization: "Bearer tok" } });
    expect(cache.cacheTag).not.toHaveBeenCalled();
  });
});

describe("page composition", () => {
  test("request-time part is wrapped in Suspense with a fallback", async () => {
    const page = await import("./app/jobs/page");
    const tree = page.default() as ReactElement<{ children: ReactElement[] }>;
    const children = ([] as ReactElement[]).concat(tree.props.children);
    const suspense = children.find((child) => isValidElement(child) && child.type === Suspense) as ReactElement<{ fallback: ReactElement; children: ReactElement }> | undefined;
    expect(suspense, "wrap MyApplicationsSummary in <Suspense>").toBeDefined();
    expect(suspense!.props.children.type).toBe(page.MyApplicationsSummary);
    render(suspense!.props.fallback);
    expect(screen.getByRole("status")).toHaveTextContent("Loading your applications…");
    expect(children.some((child) => isValidElement(child) && child.type === page.JobList)).toBe(true);
  });

  test("JobList and summary render", async () => {
    vi.stubGlobal("fetch", vi.fn(async (url: string) => json(200, { data: url.endsWith("/jobs") ? [{ id: 1, title: "AI Engineer", company: "Lintas" }] : [{ id: 1 }, { id: 2 }] })));
    const { JobList, MyApplicationsSummary } = await import("./app/jobs/page");
    render(await JobList());
    expect(screen.getByRole("listitem")).toHaveTextContent("AI Engineer");
    render(await MyApplicationsSummary());
    expect(screen.getByText("Log in to track applications")).toBeInTheDocument();
    cache.cookie = "user-token";
    render(await MyApplicationsSummary());
    expect(screen.getByText("You have 2 applications")).toBeInTheDocument();
  });
});

describe("server action", () => {
  test("is a use server file", () => {
    expect(source("app/actions.ts").trimStart()).toMatch(/^["']use server["']/);
  });

  test("requires a session and doesn't call the API without one", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const { closeJob } = await import("./app/actions");
    await expect(closeJob(3)).resolves.toEqual({ ok: false, message: "Please log in" });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  test("expires tags only after a successful mutation", async () => {
    cache.cookie = "admin-token";
    const fetchMock = vi.fn().mockResolvedValueOnce(json(500, {})).mockResolvedValueOnce(json(200, { data: {} }));
    vi.stubGlobal("fetch", fetchMock);
    const { closeJob } = await import("./app/actions");
    await expect(closeJob(3)).resolves.toEqual({ ok: false, message: "Couldn't close the job" });
    expect(cache.updateTag).not.toHaveBeenCalled();
    await expect(closeJob(3)).resolves.toEqual({ ok: true });
    expect(fetchMock).toHaveBeenLastCalledWith("http://flask:5091/api/v1/jobs/3/close", { method: "POST", headers: { Authorization: "Bearer admin-token" } });
    expect(cache.updateTag.mock.calls).toEqual([["jobs"], ["job-3"]]);
  });
});

test("types", () => {
  expect(typecheckFolder(import.meta.dirname, { recursive: true }).output).toBe("");
});

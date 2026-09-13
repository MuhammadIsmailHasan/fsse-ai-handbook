import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { isValidElement, type ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";

vi.mock("server-only", () => ({}));
vi.mock("next/navigation", () => ({ notFound: () => { throw new Error("NEXT_NOT_FOUND"); } }));
const clientApi = vi.hoisted(() => ({ saveJob: vi.fn() }));
vi.mock("./lib/client-api", () => clientApi);

const dir = (...p: string[]) => join(import.meta.dirname, ...p);
const read = (p: string) => (existsSync(dir(p)) ? readFileSync(dir(p), "utf8") : "");
const JOB = { id: 5, title: "AI Engineer", company: "Lintas AI", description: "Build RAG features.\n\nWork with evals.", saved: false };
const json = (status: number, body: unknown) => new Response(JSON.stringify(body), { status });

beforeEach(() => {
  vi.stubEnv("API_URL", "http://flask:5091");
  vi.stubEnv("API_TOKEN", "server-secret-token-123");
  clientApi.saveJob.mockReset();
});
afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

describe("where code runs", () => {
  test("page and description are Server Components", () => {
    const page = read("app/jobs/[id]/page.tsx");
    expect(page).not.toMatch(/["']use client["']/);
    expect(page).not.toMatch(/\buse(State|Effect)\b/);
    expect(page).toMatch(/export default async function/);
    expect(read("app/jobs/[id]/job-description.tsx")).not.toMatch(/["']use client["']|\buseState\b/);
  });

  test("client islands are marked and never touch server secrets", () => {
    for (const file of ["app/jobs/[id]/save-job-button.tsx", "app/jobs/[id]/share-button.tsx"]) {
      const source = read(file);
      expect(source.trimStart(), file).toMatch(/^["']use client["']/);
      expect(source, file).not.toMatch(/lib\/data/);
      expect(source.replace(/process\.env\.NEXT_PUBLIC_\w+/g, ""), file).not.toMatch(/process\.env/);
    }
  });

  test("data access is server-only", () => {
    const data = read("lib/data.ts");
    expect(data).toMatch(/^import ["']server-only["'];?/m);
    expect(data).toContain("process.env.API_TOKEN");
  });
});

describe("data access", () => {
  test("getJob sends the token from the server and handles 404", async () => {
    const fetchMock = vi.fn(async (url: string) => (url.endsWith("/5") ? json(200, { data: JOB }) : json(404, { error: { code: "not_found" } })));
    vi.stubGlobal("fetch", fetchMock);
    const { getJob } = await import("./lib/data");
    await expect(getJob(5)).resolves.toEqual(JOB);
    expect(fetchMock).toHaveBeenCalledWith("http://flask:5091/api/v1/jobs/5", { headers: { Authorization: "Bearer server-secret-token-123" } });
    await expect(getJob(99)).resolves.toBeNull();
  });
});

function collectClientProps(node: ReactNode, names: string[], found: Record<string, unknown>[] = []) {
  if (Array.isArray(node)) node.forEach((child) => collectClientProps(child, names, found));
  else if (isValidElement(node)) {
    const type = node.type as { name?: string };
    const props = node.props as Record<string, unknown> & { children?: ReactNode };
    if (type.name && names.includes(type.name)) found.push(props);
    collectClientProps(props.children, names, found);
  }
  return found;
}

describe("the page", () => {
  test("renders server data with client islands and serializable props", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json(200, { data: JOB })));
    const { default: Page } = await import("./app/jobs/[id]/page");
    const tree = await Page({ params: Promise.resolve({ id: "5" }) });

    const islandProps = collectClientProps(tree, ["SaveJobButton", "ShareButton"]);
    expect(islandProps).toEqual([{ jobId: 5, initialSaved: false }, { url: "https://careerpilot.id/jobs/5" }]);
    for (const props of islandProps) for (const value of Object.values(props)) expect(typeof value).not.toBe("function");

    render(tree);
    expect(screen.getByRole("heading", { level: 1, name: "AI Engineer" })).toBeInTheDocument();
    expect(screen.getByText("Build RAG features.")).toBeInTheDocument();
    expect(screen.getByText("Work with evals.")).toBeInTheDocument();
  });

  test("missing job → notFound", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json(404, {})));
    const { default: Page } = await import("./app/jobs/[id]/page");
    await expect(Page({ params: Promise.resolve({ id: "404" }) })).rejects.toThrow("NEXT_NOT_FOUND");
  });
});

describe("client islands", () => {
  test("SaveJobButton saves optimistically and rolls back on failure", async () => {
    const { SaveJobButton } = await import("./app/jobs/[id]/save-job-button");
    const user = userEvent.setup();
    clientApi.saveJob.mockResolvedValueOnce(undefined).mockRejectedValueOnce(new Error("offline"));
    render(<SaveJobButton jobId={5} initialSaved={false} />);
    await user.click(screen.getByRole("button", { name: "Save job" }));
    expect(clientApi.saveJob).toHaveBeenLastCalledWith(5, true);
    expect(screen.getByRole("button", { name: "Saved" })).toHaveAttribute("aria-pressed", "true");
    await user.click(screen.getByRole("button", { name: "Saved" }));
    expect(clientApi.saveJob).toHaveBeenLastCalledWith(5, false);
    await vi.waitFor(() => expect(screen.getByRole("button", { name: "Saved" })).toBeInTheDocument());
  });

  test("ShareButton copies the link", async () => {
    const writeText = vi.fn(async () => {});
    const user = userEvent.setup();
    Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
    const { ShareButton } = await import("./app/jobs/[id]/share-button");
    render(<ShareButton url="https://careerpilot.id/jobs/5" />);
    await user.click(screen.getByRole("button", { name: "Copy link" }));
    expect(writeText).toHaveBeenCalledWith("https://careerpilot.id/jobs/5");
    expect(await screen.findByRole("button", { name: "Link copied" })).toBeInTheDocument();
  });
});

test("types", () => {
  expect(typecheckFolder(import.meta.dirname, { recursive: true }).output).toBe("");
});

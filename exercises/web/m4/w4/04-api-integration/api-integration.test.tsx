import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { readFileSync } from "node:fs";
import { beforeEach, describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";

const mocks = vi.hoisted(() => ({
  listApplications: vi.fn(),
  redirect: vi.fn((url: string) => {
    throw new Error(`NEXT_REDIRECT ${url}`);
  }),
}));
vi.mock("next/navigation", () => ({ redirect: mocks.redirect, notFound: vi.fn() }));
vi.mock("./lib/server-api", () => ({ getServerApi: async () => ({ listApplications: mocks.listApplications }) }));

import { ApiError, createApiClient } from "./lib/api-client";

const json = (status: number, body: unknown) => new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
const APP = { id: 7, role: "Backend Engineer", status: "applied", company: { id: 3, name: "Kopi Data" } };

describe("api client", () => {
  test("list sends auth, query and no-store", async () => {
    const fetchImpl = vi.fn(async () => json(200, { data: [APP], meta: { page: 2, per_page: 20, total: 21 } }));
    const api = createApiClient({ baseUrl: "http://localhost:5091", getToken: () => "tok", fetchImpl });
    await expect(api.listApplications({ status: "applied", page: 2 })).resolves.toEqual({ data: [APP], meta: { page: 2, per_page: 20, total: 21 } });
    const [url, init] = fetchImpl.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("http://localhost:5091/api/v1/applications?status=applied&page=2");
    expect(init.headers).toEqual({ Accept: "application/json", Authorization: "Bearer tok" });
    expect(init.cache).toBe("no-store");
  });

  test("no token, no params, and getApplication unwraps data", async () => {
    const fetchImpl = vi.fn(async (url: string) => (url.endsWith("/7") ? json(200, { data: APP }) : json(200, { data: [], meta: { page: 1, per_page: 20, total: 0 } })));
    const api = createApiClient({ baseUrl: "http://localhost:5091", getToken: () => undefined, fetchImpl: fetchImpl as unknown as typeof fetch });
    await api.listApplications();
    expect(fetchImpl.mock.calls[0]![0]).toBe("http://localhost:5091/api/v1/applications");
    expect((fetchImpl.mock.calls[0] as unknown as [string, RequestInit])[1].headers).toEqual({ Accept: "application/json" });
    await expect(api.getApplication(7)).resolves.toEqual(APP);
  });

  test("maps API errors", async () => {
    const api = (response: Response | Error) =>
      createApiClient({ baseUrl: "http://x", getToken: () => "t", fetchImpl: (async () => { if (response instanceof Error) throw response; return response; }) as typeof fetch });
    const validation = await api(json(422, { error: { code: "validation_failed", message: "Invalid request", fields: { status: ["Not a valid choice."] } } })).listApplications().catch((e) => e);
    expect(validation).toBeInstanceOf(ApiError);
    expect(validation).toMatchObject({ name: "ApiError", status: 422, code: "validation_failed", message: "Invalid request", fields: { status: ["Not a valid choice."] } });
    const html = await api(new Response("<h1>Bad gateway</h1>", { status: 502 })).listApplications().catch((e) => e);
    expect(html).toMatchObject({ status: 502, code: "unknown_error" });
    const offline = await api(new TypeError("fetch failed")).listApplications().catch((e) => e);
    expect(offline).toMatchObject({ status: 0, code: "network_error" });
  });
});

describe("applications page", () => {
  beforeEach(() => {
    mocks.listApplications.mockReset();
    mocks.redirect.mockClear();
  });

  const renderPage = async (searchParams: Record<string, string>) => {
    const { default: Page } = await import("./app/applications/page");
    render(await Page({ searchParams: Promise.resolve(searchParams) }));
  };

  test("validates search params before calling the API", async () => {
    mocks.listApplications.mockResolvedValue({ data: [APP], meta: { page: 2, per_page: 20, total: 41 } });
    await renderPage({ status: "applied", page: "2" });
    expect(mocks.listApplications).toHaveBeenLastCalledWith({ status: "applied", page: 2 });
    expect(screen.getByRole("heading", { level: 1, name: "Applications" })).toBeInTheDocument();
    expect(screen.getByRole("listitem")).toHaveTextContent("Backend Engineer at Kopi Data");
    expect(screen.getByText("Page 2 of 3")).toBeInTheDocument();
  });

  test("ignores invalid params", async () => {
    mocks.listApplications.mockResolvedValue({ data: [], meta: { page: 1, per_page: 20, total: 0 } });
    await renderPage({ status: "ghosted", page: "-4" });
    const filters = mocks.listApplications.mock.calls[0]![0];
    expect(filters.status).toBeUndefined();
    expect(filters.page === undefined || filters.page === 1).toBe(true);
    expect(screen.getByText("No applications found")).toBeInTheDocument();
  });

  test("401 redirects to login, other errors bubble to the error boundary", async () => {
    mocks.listApplications.mockRejectedValue(new ApiError(401, "unauthorized", "Token expired"));
    await expect(renderPage({})).rejects.toThrow("NEXT_REDIRECT /login?next=/applications");
    mocks.listApplications.mockRejectedValue(new ApiError(500, "internal_error", "boom"));
    await expect(renderPage({})).rejects.toMatchObject({ status: 500 });
    expect(mocks.redirect).toHaveBeenCalledTimes(1);
  });
});

describe("error and loading UI", () => {
  test("error boundary logs and retries", async () => {
    const consoleError = vi.spyOn(console, "error").mockImplementation(() => {});
    const { default: ErrorUI } = await import("./app/applications/error");
    const retry = vi.fn();
    const error = new Error("boom");
    render(<ErrorUI error={error} retry={retry} />);
    expect(screen.getByRole("alert")).toHaveTextContent("We couldn't load your applications");
    await userEvent.setup().click(screen.getByRole("button", { name: "Try again" }));
    expect(retry).toHaveBeenCalledTimes(1);
    expect(consoleError).toHaveBeenCalledWith(error);
    expect(readFileSync(`${import.meta.dirname}/app/applications/error.tsx`, "utf8").trimStart()).toMatch(/^["']use client["']/);
  });

  test("loading UI", async () => {
    const { default: Loading } = await import("./app/applications/loading");
    render(<Loading />);
    expect(screen.getByRole("status")).toHaveTextContent("Loading applications…");
  });
});

test("types", () => {
  expect(typecheckFolder(import.meta.dirname, { recursive: true }).output).toBe("");
});

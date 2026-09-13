// @vitest-environment node
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";

const mocks = vi.hoisted(() => ({ getSession: vi.fn() }));
vi.mock("./lib/session", () => ({ getSession: mocks.getSession }));

import * as collection from "./app/api/applications/route";
import * as item from "./app/api/applications/[id]/route";
import { ApiError, applicationsClient } from "./lib/applications-client";

const fetchMock = vi.fn();
const ctx = (id: string) => ({ params: Promise.resolve({ id }) });
const jsonRequest = (url: string, method: string, body: string) => new Request(url, { method, body, headers: { "Content-Type": "application/json" } });

beforeEach(() => {
  vi.stubEnv("API_URL", "http://flask:5091");
  vi.stubGlobal("fetch", fetchMock);
  fetchMock.mockReset();
  mocks.getSession.mockReset().mockResolvedValue({ accessToken: "tok-9" });
});
afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

describe("route handlers", () => {
  test("GET list forwards query string with bearer token and no-store", async () => {
    fetchMock.mockResolvedValueOnce(new Response('[{"id":1}]', { status: 200 }));
    const response = await collection.GET(new Request("http://localhost:3091/api/applications?status=applied&page=2"));
    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toContain("application/json");
    expect(await response.json()).toEqual([{ id: 1 }]);
    const [url, init] = fetchMock.mock.calls[0]!;
    expect(url).toBe("http://flask:5091/api/v1/applications?status=applied&page=2");
    expect(init).toMatchObject({ method: "GET", cache: "no-store" });
    expect(init.headers).toEqual({ Authorization: "Bearer tok-9", Accept: "application/json" });
    expect(init.body).toBeUndefined();
  });

  test("401 without a session, never calling Flask", async () => {
    mocks.getSession.mockResolvedValue(null);
    const response = await collection.GET(new Request("http://localhost:3091/api/applications"));
    expect(response.status).toBe(401);
    expect(await response.json()).toEqual({ error: { code: "unauthenticated" } });
    expect((await item.DELETE(new Request("http://x/api/applications/1", { method: "DELETE" }), ctx("1"))).status).toBe(401);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  test("POST forwards JSON and passes through status and error bodies", async () => {
    fetchMock.mockResolvedValueOnce(new Response('{"id":5}', { status: 201 }));
    const created = await collection.POST(jsonRequest("http://x/api/applications", "POST", '{"role":"Dev","company_id":2}'));
    expect(created.status).toBe(201);
    const [, init] = fetchMock.mock.calls[0]!;
    expect(init.method).toBe("POST");
    expect(init.headers["Content-Type"]).toBe("application/json");
    expect(JSON.parse(init.body)).toEqual({ role: "Dev", company_id: 2 });

    fetchMock.mockResolvedValueOnce(new Response('{"error":{"code":"validation_failed","fields":{"role":["Required"]}}}', { status: 422 }));
    const invalid = await collection.POST(jsonRequest("http://x/api/applications", "POST", '{"role":""}'));
    expect(invalid.status).toBe(422);
    expect(await invalid.json()).toEqual({ error: { code: "validation_failed", fields: { role: ["Required"] } } });
  });

  test("invalid JSON → 400", async () => {
    const response = await collection.POST(jsonRequest("http://x/api/applications", "POST", "{nope"));
    expect(response.status).toBe(400);
    expect(await response.json()).toEqual({ error: { code: "invalid_json" } });
    expect((await item.PATCH(jsonRequest("http://x/api/applications/1", "PATCH", "nope"), ctx("1"))).status).toBe(400);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  test("item routes validate the id and use the right methods", async () => {
    for (const bad of ["abc", "1;DROP", "..%2Fusers", "-1", ""]) {
      const response = await item.GET(new Request("http://x"), ctx(bad));
      expect(response.status, bad).toBe(400);
      expect(await response.json()).toEqual({ error: { code: "invalid_id" } });
    }
    expect(fetchMock).not.toHaveBeenCalled();

    fetchMock.mockResolvedValueOnce(new Response('{"id":7}', { status: 200 }));
    await item.GET(new Request("http://x"), ctx("7"));
    fetchMock.mockResolvedValueOnce(new Response('{"id":7,"status":"offer"}', { status: 200 }));
    const patched = await item.PATCH(jsonRequest("http://x", "PATCH", '{"status":"offer"}'), ctx("7"));
    expect(await patched.json()).toEqual({ id: 7, status: "offer" });
    fetchMock.mockResolvedValueOnce(new Response(null, { status: 204 }));
    const deleted = await item.DELETE(new Request("http://x", { method: "DELETE" }), ctx("7"));
    expect(deleted.status).toBe(204);
    expect(await deleted.text()).toBe("");
    expect(fetchMock.mock.calls.map(([url, init]) => `${init.method} ${url}`)).toEqual([
      "GET http://flask:5091/api/v1/applications/7",
      "PATCH http://flask:5091/api/v1/applications/7",
      "DELETE http://flask:5091/api/v1/applications/7",
    ]);
  });

  test("network failure → 502 without leaking details", async () => {
    fetchMock.mockRejectedValueOnce(new TypeError("connect ECONNREFUSED 10.0.0.5:5091"));
    const response = await collection.GET(new Request("http://x/api/applications"));
    expect(response.status).toBe(502);
    const text = await response.text();
    expect(JSON.parse(text)).toEqual({ error: { code: "upstream_unavailable" } });
    expect(text).not.toContain("ECONNREFUSED");
  });
});

describe("browser client", () => {
  test("methods, URLs, headers and bodies", async () => {
    fetchMock.mockImplementation(async () => new Response("[]", { status: 200 }));
    await applicationsClient.list();
    await applicationsClient.list("in review");
    await applicationsClient.create({ company_id: 2, role: "Dev" });
    await applicationsClient.update(3, { status: "offer" });
    fetchMock.mockResolvedValueOnce(new Response(null, { status: 204 }));
    await expect(applicationsClient.remove(3)).resolves.toBeNull();
    expect(fetchMock.mock.calls.map(([url, init]) => `${init?.method ?? "GET"} ${url}`)).toEqual([
      "GET /api/applications",
      "GET /api/applications?status=in%20review",
      "POST /api/applications",
      "PATCH /api/applications/3",
      "DELETE /api/applications/3",
    ]);
    const post = fetchMock.mock.calls[2]![1];
    expect(post.headers["Content-Type"]).toBe("application/json");
    expect(JSON.parse(post.body)).toEqual({ company_id: 2, role: "Dev" });
    expect(fetchMock.mock.calls[0]![1].headers?.["Content-Type"]).toBeUndefined();
  });

  test("errors", async () => {
    fetchMock.mockResolvedValueOnce(new Response('{"error":{"code":"not_found"}}', { status: 404 }));
    const error = await applicationsClient.update(99, { role: "x" }).catch((e) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ status: 404, code: "not_found" });
    fetchMock.mockResolvedValueOnce(new Response("<html>Bad gateway</html>", { status: 502 }));
    await expect(applicationsClient.list()).rejects.toMatchObject({ status: 502, code: "unknown_error" });
  });
});

test("types", () => {
  expect(typecheckFolder(import.meta.dirname, { recursive: true }).output).toBe("");
});

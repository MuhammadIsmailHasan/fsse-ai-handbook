import { afterEach, describe, expect, test, vi } from "vitest";
import { ApiError, TimeoutError, getJson, getJsonWithTimeout, loadCompanies, loadDashboard, withRetry } from "./api-client.js";

const json = (status, body) => new Response(body === undefined ? null : JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });

describe("getJson", () => {
  test("returns parsed JSON and sends Accept + custom headers", async () => {
    const fetchImpl = vi.fn(async () => json(200, { data: [1] }));
    await expect(getJson(fetchImpl, "/api/v1/jobs", { headers: { Authorization: "Bearer t" } })).resolves.toEqual({ data: [1] });
    const [url, init] = fetchImpl.mock.calls[0];
    expect(url).toBe("/api/v1/jobs");
    expect(init.headers).toEqual({ Accept: "application/json", Authorization: "Bearer t" });
  });

  test("204 is null", async () => {
    await expect(getJson(async () => new Response(null, { status: 204 }), "/x")).resolves.toBeNull();
  });

  test("non-2xx throws ApiError with body", async () => {
    const error = await getJson(async () => json(404, { error: { code: "not_found" } }), "/x").catch((e) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toBeInstanceOf(Error);
    expect(error).toMatchObject({ name: "ApiError", status: 404, body: { error: { code: "not_found" } }, message: "Request failed with status 404" });
    const html = await getJson(async () => new Response("<h1>Bad Gateway</h1>", { status: 502 }), "/x").catch((e) => e);
    expect(html).toMatchObject({ status: 502, body: null });
  });
});

describe("getJsonWithTimeout", () => {
  afterEach(() => vi.useRealTimers());

  test("aborts slow requests", async () => {
    vi.useFakeTimers();
    const slowFetch = (url, { signal }) =>
      new Promise((resolve, reject) => {
        const t = setTimeout(() => resolve(json(200, {})), 5_000);
        signal.addEventListener("abort", () => {
          clearTimeout(t);
          reject(new DOMException("aborted", "AbortError"));
        });
      });
    const pending = getJsonWithTimeout(slowFetch, "/slow", 1_000).catch((e) => e);
    await vi.advanceTimersByTimeAsync(1_000);
    const error = await pending;
    expect(error).toBeInstanceOf(TimeoutError);
    expect(error.name).toBe("TimeoutError");
    expect(vi.getTimerCount()).toBe(0);
  });

  test("fast requests succeed and clear the timer", async () => {
    vi.useFakeTimers();
    await expect(getJsonWithTimeout(async () => json(200, { ok: true }), "/fast", 1_000)).resolves.toEqual({ ok: true });
    expect(vi.getTimerCount()).toBe(0);
  });

  test("other errors pass through", async () => {
    await expect(getJsonWithTimeout(async () => json(401, {}), "/x", 1_000)).rejects.toBeInstanceOf(ApiError);
  });
});

test("loadDashboard runs requests in parallel", async () => {
  let inFlight = 0;
  let maxInFlight = 0;
  const fetchImpl = async (url) => {
    inFlight++;
    maxInFlight = Math.max(maxInFlight, inFlight);
    await new Promise((r) => setTimeout(r, 10));
    inFlight--;
    const path = new URL(url).pathname;
    return json(200, { data: { "/api/v1/me": { id: 7 }, "/api/v1/applications": [{ id: 1 }], "/api/v1/stats": { total: 1 } }[path] });
  };
  await expect(loadDashboard(fetchImpl, "http://localhost:5091")).resolves.toEqual({ user: { id: 7 }, applications: [{ id: 1 }], stats: { total: 1 } });
  expect(maxInFlight).toBe(3);
});

test("loadCompanies tolerates partial failures", async () => {
  const fetchImpl = async (url) => {
    const id = Number(url.split("/").pop());
    if (id === 2) return json(404, {});
    if (id === 4) throw new TypeError("Failed to fetch");
    return json(200, { data: { id, name: `Company ${id}` } });
  };
  await expect(loadCompanies(fetchImpl, "", [1, 2, 3, 4])).resolves.toEqual({
    companies: [{ id: 1, name: "Company 1" }, { id: 3, name: "Company 3" }],
    failedIds: [2, 4],
  });
});

describe("withRetry", () => {
  test("retries server and network errors with exponential backoff", async () => {
    const sleep = vi.fn(async () => {});
    const fn = vi
      .fn()
      .mockRejectedValueOnce(new ApiError(503, null))
      .mockRejectedValueOnce(new TypeError("Failed to fetch"))
      .mockResolvedValueOnce("ok");
    await expect(withRetry(fn, { attempts: 3, delayMs: 100, sleep })).resolves.toBe("ok");
    expect(sleep.mock.calls).toEqual([[100], [200]]);
  });

  test("does not retry client errors, and gives up after the last attempt", async () => {
    const sleep = vi.fn(async () => {});
    const clientError = vi.fn().mockRejectedValue(new ApiError(422, {}));
    await expect(withRetry(clientError, { sleep })).rejects.toMatchObject({ status: 422 });
    expect(clientError).toHaveBeenCalledTimes(1);
    const alwaysDown = vi.fn().mockRejectedValue(new ApiError(500, null));
    await expect(withRetry(alwaysDown, { attempts: 2, sleep })).rejects.toMatchObject({ status: 500 });
    expect(alwaysDown).toHaveBeenCalledTimes(2);
    expect(sleep).toHaveBeenCalledTimes(1);
  });
});

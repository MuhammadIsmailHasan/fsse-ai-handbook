import { render } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { afterEach, describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";

const hook = vi.hoisted(() => ({ useReportWebVitals: vi.fn() }));
vi.mock("next/web-vitals", () => hook);

import { reportWebVital, WebVitals } from "./app/_components/web-vitals";
import { POST } from "./app/api/vitals/route";
import { formatMetric, p75, rateMetric, summarize, THRESHOLDS } from "./lib/vitals";

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
  hook.useReportWebVitals.mockReset();
});

describe("vitals math", () => {
  test("thresholds and ratings at the boundaries", () => {
    expect(THRESHOLDS).toEqual({ LCP: [2500, 4000], INP: [200, 500], CLS: [0.1, 0.25], FCP: [1800, 3000], TTFB: [800, 1800] });
    expect(rateMetric("LCP", 2500)).toBe("good");
    expect(rateMetric("LCP", 2501)).toBe("needs-improvement");
    expect(rateMetric("LCP", 4000)).toBe("needs-improvement");
    expect(rateMetric("LCP", 4001)).toBe("poor");
    expect(rateMetric("INP", 120)).toBe("good");
    expect(rateMetric("CLS", 0.3)).toBe("poor");
    expect(rateMetric("TTFB", 900)).toBe("needs-improvement");
  });

  test("formatting", () => {
    expect(formatMetric("CLS", 0.0512)).toBe("0.05");
    expect(formatMetric("LCP", 2479.6)).toBe("2480 ms");
  });

  test("p75 nearest rank", () => {
    expect(p75([])).toBeNull();
    expect(p75([100])).toBe(100);
    expect(p75([400, 100, 300, 200])).toBe(300);
    expect(p75([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])).toBe(8);
  });

  test("summarize", () => {
    const samples = [
      ...[1800, 2200, 2600, 4200].map((value) => ({ name: "LCP" as const, value })),
      { name: "CLS" as const, value: 0.02 },
    ];
    expect(summarize(samples)).toEqual({
      LCP: { p75: 2600, rating: "needs-improvement", count: 4 },
      CLS: { p75: 0.02, rating: "good", count: 1 },
    });
  });
});

describe("reporting component", () => {
  const metric = { name: "LCP", value: 2300, rating: "good", id: "v5-1", navigationType: "navigate", delta: 2300, entries: [] };

  test("registers a stable module-level callback", () => {
    const { rerender } = render(<WebVitals />);
    rerender(<WebVitals />);
    expect(hook.useReportWebVitals).toHaveBeenCalledTimes(2);
    expect(hook.useReportWebVitals.mock.calls[0]![0]).toBe(reportWebVital);
    expect(hook.useReportWebVitals.mock.calls[1]![0]).toBe(reportWebVital);
    expect(readFileSync(`${import.meta.dirname}/app/_components/web-vitals.tsx`, "utf8").trimStart()).toMatch(/^["']use client["']/);
  });

  test("uses sendBeacon when available", () => {
    const sendBeacon = vi.fn(() => true);
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    Object.defineProperty(navigator, "sendBeacon", { value: sendBeacon, configurable: true });
    window.history.pushState({}, "", "/jobs/7");
    reportWebVital(metric);
    expect(sendBeacon).toHaveBeenCalledTimes(1);
    const [url, body] = sendBeacon.mock.calls[0] as unknown as [string, string];
    expect(url).toBe("/api/vitals");
    expect(JSON.parse(body)).toEqual({ name: "LCP", value: 2300, rating: "good", id: "v5-1", navigationType: "navigate", path: "/jobs/7" });
    expect(fetchMock).not.toHaveBeenCalled();
    Object.defineProperty(navigator, "sendBeacon", { value: undefined, configurable: true });
  });

  test("falls back to fetch with keepalive", () => {
    Object.defineProperty(navigator, "sendBeacon", { value: undefined, configurable: true });
    const fetchMock = vi.fn(() => Promise.resolve(new Response(null, { status: 204 })));
    vi.stubGlobal("fetch", fetchMock);
    reportWebVital(metric);
    expect(fetchMock).toHaveBeenCalledWith("/api/vitals", expect.objectContaining({ method: "POST", keepalive: true, headers: { "Content-Type": "application/json" } }));
  });
});

describe("collector endpoint", () => {
  const post = (body: string, headers: Record<string, string> = {}) =>
    POST(new Request("http://localhost/api/vitals", { method: "POST", body, headers: { "Content-Type": "application/json", ...headers } }));
  const valid = { name: "INP", value: 180, rating: "good", id: "v5-9", navigationType: "navigate", path: "/applications" };

  test("logs one structured line and returns 204", async () => {
    const info = vi.spyOn(console, "info").mockImplementation(() => {});
    const response = await post(JSON.stringify(valid));
    expect(response.status).toBe(204);
    expect(info).toHaveBeenCalledTimes(1);
    expect(JSON.parse(info.mock.calls[0]![0] as string)).toEqual({ event: "web_vital", ...valid });
  });

  test("rejects bad input", async () => {
    const info = vi.spyOn(console, "info").mockImplementation(() => {});
    expect((await post("{nope")).status).toBe(400);
    for (const bad of [{ ...valid, name: "FID" }, { ...valid, value: -1 }, { ...valid, rating: "great" }, { ...valid, path: "https://evil.example" }, { ...valid, id: "x".repeat(101) }]) {
      expect((await post(JSON.stringify(bad))).status, JSON.stringify(bad)).toBe(400);
    }
    expect((await post(JSON.stringify(valid), { "Content-Length": "5000" })).status).toBe(413);
    expect(info).not.toHaveBeenCalled();
  });
});

test("types", () => {
  expect(typecheckFolder(import.meta.dirname, { recursive: true }).output).toBe("");
});

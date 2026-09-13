import { act, render, renderHook, screen, waitFor } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { renderToString } from "react-dom/server";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import { useDebouncedValue, useFetchJson, useLocalStorage, useOnlineStatus } from "./hooks";
import { JobCount } from "./job-count";

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
  localStorage.clear();
});

test("useDebouncedValue", () => {
  vi.useFakeTimers();
  const { result, rerender, unmount } = renderHook(({ value }) => useDebouncedValue(value, 300), { initialProps: { value: "d" } });
  expect(result.current).toBe("d");
  rerender({ value: "da" });
  act(() => vi.advanceTimersByTime(200));
  rerender({ value: "dat" });
  act(() => vi.advanceTimersByTime(200));
  expect(result.current).toBe("d");
  act(() => vi.advanceTimersByTime(100));
  expect(result.current).toBe("dat");
  rerender({ value: "data" });
  unmount();
  expect(vi.getTimerCount()).toBe(0);
});

describe("useOnlineStatus", () => {
  test("follows browser events and cleans up", () => {
    let online = true;
    vi.spyOn(navigator, "onLine", "get").mockImplementation(() => online);
    const removeSpy = vi.spyOn(window, "removeEventListener");
    const { result, unmount } = renderHook(() => useOnlineStatus());
    expect(result.current).toBe(true);
    act(() => {
      online = false;
      window.dispatchEvent(new Event("offline"));
    });
    expect(result.current).toBe(false);
    act(() => {
      online = true;
      window.dispatchEvent(new Event("online"));
    });
    expect(result.current).toBe(true);
    unmount();
    expect(removeSpy.mock.calls.map((c) => c[0])).toEqual(expect.arrayContaining(["online", "offline"]));
  });

  test("uses useSyncExternalStore with a server snapshot", () => {
    const source = readFileSync(`${import.meta.dirname}/hooks.ts`, "utf8");
    expect(source).toMatch(/useSyncExternalStore\(/);
    vi.spyOn(navigator, "onLine", "get").mockReturnValue(false);
    function Badge() {
      return <span>{useOnlineStatus() ? "online" : "offline"}</span>;
    }
    expect(renderToString(<Badge />)).toContain("online");
  });
});

describe("useFetchJson", () => {
  type Deferred = { url: string; signal: AbortSignal; resolve: (r: Response) => void };
  let requests: Deferred[];
  beforeEach(() => {
    requests = [];
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string, init: RequestInit) => {
        return new Promise<Response>((resolve, reject) => {
          init.signal!.addEventListener("abort", () => reject(new DOMException("Aborted", "AbortError")));
          requests.push({ url, signal: init.signal!, resolve });
        });
      }),
    );
  });

  test("idle for null, then loading and success", async () => {
    const { result, rerender } = renderHook(({ url }) => useFetchJson<{ id: number }[]>(url), { initialProps: { url: null as string | null } });
    expect(result.current).toEqual({ status: "idle", data: null, error: null });
    expect(fetch).not.toHaveBeenCalled();
    rerender({ url: "/api/jobs" });
    expect(result.current.status).toBe("loading");
    await act(async () => requests[0]!.resolve(Response.json([{ id: 1 }])));
    await waitFor(() => expect(result.current).toEqual({ status: "success", data: [{ id: 1 }], error: null }));
  });

  test("aborts the old request; stale responses never win", async () => {
    const { result, rerender, unmount } = renderHook(({ url }) => useFetchJson<string>(url), { initialProps: { url: "/api/jobs?q=d" as string | null } });
    rerender({ url: "/api/jobs?q=data" });
    expect(requests[0]!.signal.aborted).toBe(true);
    expect(result.current.status).toBe("loading");
    await act(async () => requests[1]!.resolve(Response.json("new")));
    await waitFor(() => expect(result.current.data).toBe("new"));
    await act(async () => requests[0]!.resolve(Response.json("old")));
    expect(result.current.data).toBe("new");
    rerender({ url: "/api/jobs?q=x" });
    unmount();
    expect(requests[2]!.signal.aborted).toBe(true);
  });

  test("HTTP errors", async () => {
    const { result } = renderHook(() => useFetchJson("/api/jobs"));
    await act(async () => requests[0]!.resolve(new Response("nope", { status: 503 })));
    await waitFor(() => expect(result.current).toEqual({ status: "error", data: null, error: "Request failed with status 503" }));
  });
});

describe("useLocalStorage", () => {
  test("SSR-safe first render, then reads storage", async () => {
    localStorage.setItem("cp:view", JSON.stringify("board"));
    function View() {
      const [view] = useLocalStorage("cp:view", "list");
      return <span>{view}</span>;
    }
    expect(renderToString(<View />)).toContain("list");
    render(<View />);
    expect(await screen.findByText("board")).toBeInTheDocument();
  });

  test("writes, handles bad JSON and syncs across tabs", async () => {
    localStorage.setItem("cp:compare", "{broken");
    const removeSpy = vi.spyOn(window, "removeEventListener");
    const { result, unmount } = renderHook(() => useLocalStorage<number[]>("cp:compare", []));
    expect(result.current[0]).toEqual([]);
    act(() => result.current[1]([4, 8]));
    expect(result.current[0]).toEqual([4, 8]);
    expect(localStorage.getItem("cp:compare")).toBe("[4,8]");
    act(() => {
      localStorage.setItem("cp:compare", "[1]");
      window.dispatchEvent(new StorageEvent("storage", { key: "other", newValue: "[]" }));
    });
    expect(result.current[0]).toEqual([4, 8]);
    act(() => {
      window.dispatchEvent(new StorageEvent("storage", { key: "cp:compare", newValue: "[1]" }));
    });
    expect(result.current[0]).toEqual([1]);
    unmount();
    expect(removeSpy.mock.calls.map((c) => c[0])).toContain("storage");
  });
});

test("JobCount derives during render", () => {
  const jobs = [{ title: "Data Engineer" }, { title: "Frontend Developer" }, { title: "Big DATA Analyst" }];
  const { rerender } = render(<JobCount jobs={jobs} query=" data " />);
  expect(screen.getByText("2 matching jobs")).toBeInTheDocument();
  rerender(<JobCount jobs={jobs} query="" />);
  expect(screen.getByText("3 matching jobs")).toBeInTheDocument();
  const source = readFileSync(`${import.meta.dirname}/job-count.tsx`, "utf8");
  expect(source).not.toMatch(/useEffect|useState/);
});

test("types", () => {
  expect(typecheckFolder(import.meta.dirname).output).toBe("");
});

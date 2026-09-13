import { act, fireEvent, render, renderHook, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { readFileSync } from "node:fs";
import { memo, useState, type ReactNode } from "react";
import { afterEach, describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import { createStrictContext, FiltersProvider, filtersReducer, ToastProvider, useFilters, useFiltersDispatch, useToast } from "./context-kit";

afterEach(() => vi.useRealTimers());

describe("createStrictContext", () => {
  test("throws a helpful error without a provider", () => {
    const [, useCount] = createStrictContext<number>("Count");
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});
    expect(() => renderHook(() => useCount())).toThrow("useCount must be used inside <CountProvider>");
    spy.mockRestore();
  });

  test("provides values, including falsy ones", () => {
    const [CountProvider, useCount] = createStrictContext<number>("Count");
    const wrapper = ({ children }: { children: ReactNode }) => <CountProvider value={0}>{children}</CountProvider>;
    expect(renderHook(() => useCount(), { wrapper }).result.current).toBe(0);
  });
});

describe("filters", () => {
  test("reducer", () => {
    const start = { status: "all" as const, query: "" };
    expect(filtersReducer(start, { type: "setStatus", status: "offer" })).toEqual({ status: "offer", query: "" });
    const typed = filtersReducer(start, { type: "setQuery", query: "data" });
    expect(typed).toEqual({ status: "all", query: "data" });
    expect(start).toEqual({ status: "all", query: "" });
    expect(filtersReducer({ status: "rejected", query: "x" }, { type: "reset" })).toEqual({ status: "all", query: "" });
  });

  test("split contexts: dispatch-only consumers don't re-render", async () => {
    const renders = { controls: 0, summary: 0 };
    const Controls = memo(function Controls() {
      const dispatch = useFiltersDispatch();
      renders.controls++;
      return (
        <>
          <button onClick={() => dispatch({ type: "setStatus", status: "interview" })}>Interviews</button>
          <button onClick={() => dispatch({ type: "reset" })}>Reset</button>
        </>
      );
    });
    function Summary() {
      const filters = useFilters();
      renders.summary++;
      return <output>{`${filters.status}:${filters.query}`}</output>;
    }
    const user = userEvent.setup();
    render(
      <FiltersProvider initial={{ status: "applied", query: "kopi" }}>
        <Controls />
        <Summary />
      </FiltersProvider>,
    );
    expect(screen.getByRole("status")).toHaveTextContent("applied:kopi");
    await user.click(screen.getByRole("button", { name: "Interviews" }));
    expect(screen.getByRole("status")).toHaveTextContent("interview:kopi");
    await user.click(screen.getByRole("button", { name: "Reset" }));
    expect(screen.getByRole("status")).toHaveTextContent("all:");
    expect(renders.summary).toBe(3);
    expect(renders.controls).toBe(1);
  });

  test("hooks require the provider", () => {
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});
    expect(() => renderHook(() => useFilters())).toThrow(/must be used inside/);
    expect(() => renderHook(() => useFiltersDispatch())).toThrow(/must be used inside/);
    expect(() => renderHook(() => useToast())).toThrow(/must be used inside/);
    spy.mockRestore();
  });
});

describe("toasts", () => {
  function SaveButton() {
    const toast = useToast();
    return <button onClick={() => toast.show("Application saved")}>Save</button>;
  }

  test("show, auto-dismiss after 4s, and manual dismiss", () => {
    vi.useFakeTimers();
    render(
      <ToastProvider>
        <SaveButton />
      </ToastProvider>,
    );
    const region = screen.getByRole("status");
    expect(region).toHaveAttribute("aria-live", "polite");
    fireEvent.click(screen.getByRole("button", { name: "Save" }));
    fireEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(region.querySelectorAll("p")).toHaveLength(2);
    fireEvent.click(screen.getAllByRole("button", { name: "Dismiss notification" })[0]!);
    expect(region.querySelectorAll("p")).toHaveLength(1);
    act(() => vi.advanceTimersByTime(3900));
    expect(region).toHaveTextContent("Application saved");
    act(() => vi.advanceTimersByTime(200));
    expect(region.querySelectorAll("p")).toHaveLength(0);
  });

  test("api object is stable and timers are cleaned up on unmount", () => {
    vi.useFakeTimers();
    const seen = new Set<unknown>();
    function Probe() {
      const api = useToast();
      const [, setTick] = useState(0);
      seen.add(api);
      return <button onClick={() => { api.show("hi"); setTick((t) => t + 1); }}>Go</button>;
    }
    const { unmount } = render(
      <ToastProvider>
        <Probe />
      </ToastProvider>,
    );
    const button = screen.getByRole("button", { name: "Go" });
    act(() => button.click());
    act(() => button.click());
    expect(seen.size).toBe(1);
    unmount();
    expect(vi.getTimerCount()).toBe(0);
  });
});

test("client module + types", () => {
  expect(readFileSync(`${import.meta.dirname}/context-kit.tsx`, "utf8").trimStart()).toMatch(/^["']use client["']/);
  expect(typecheckFolder(import.meta.dirname).output).toBe("");
});

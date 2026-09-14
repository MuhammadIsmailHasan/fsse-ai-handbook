import { act, fireEvent, render, renderHook, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";

const nav = vi.hoisted(() => ({ query: "", push: vi.fn(), replace: vi.fn() }));
vi.mock("next/navigation", () => ({
  useSearchParams: () => new URLSearchParams(nav.query),
  usePathname: () => "/jobs",
  useRouter: () => ({ push: nav.push, replace: nav.replace }),
}));

import { JobFilterBar } from "./job-filter-bar";
import { DEFAULT_FILTERS, parseJobFilters, serializeJobFilters } from "./job-filters";
import { useJobFilters } from "./use-job-filters";

beforeEach(() => {
  nav.query = "";
  nav.push.mockReset();
  nav.replace.mockReset();
});
afterEach(() => vi.useRealTimers());

describe("parse and serialize", () => {
  test("defaults and validation", () => {
    expect(parseJobFilters(new URLSearchParams())).toEqual(DEFAULT_FILTERS);
    expect(parseJobFilters(new URLSearchParams("q=%20data%20&status=banana&remote=true&sort=salary&page=-2"))).toEqual({ q: "data", status: "open", remote: false, sort: "salary", page: 1 });
    expect(parseJobFilters({ q: ["ai", "ml"], status: "all", remote: "1", page: "3" })).toEqual({ q: "ai", status: "all", remote: true, sort: "newest", page: 3 });
    expect(parseJobFilters({ page: "2.5" }).page).toBe(1);
    expect(parseJobFilters({ q: "x".repeat(150) }).q).toHaveLength(100);
  });

  test("short, stable query strings and round trips", () => {
    expect(serializeJobFilters(DEFAULT_FILTERS)).toBe("");
    const filters = { q: "data engineer", status: "all", remote: true, sort: "salary", page: 2 } as const;
    expect(serializeJobFilters({ ...filters })).toBe("q=data+engineer&status=all&remote=1&sort=salary&page=2");
    expect(parseJobFilters(new URLSearchParams(serializeJobFilters({ ...filters })))).toEqual(filters);
    expect(serializeJobFilters({ ...DEFAULT_FILTERS, page: 3 })).toBe("page=3");
  });
});

describe("useJobFilters", () => {
  test("reads the URL and pushes changes, resetting the page", () => {
    nav.query = "q=data&page=4";
    const { result } = renderHook(() => useJobFilters());
    expect(result.current.filters).toMatchObject({ q: "data", page: 4 });
    result.current.setFilters({ remote: true });
    expect(nav.push).toHaveBeenCalledWith("/jobs?q=data&remote=1", { scroll: false });
    result.current.setFilters({ page: 5 });
    expect(nav.push).toHaveBeenLastCalledWith("/jobs?q=data&page=5", { scroll: false });
    result.current.setFilters({ q: "" }, { history: "replace" });
    expect(nav.replace).toHaveBeenCalledWith("/jobs", { scroll: false });
  });

  test("no navigation when nothing changes", () => {
    nav.query = "status=all";
    const { result } = renderHook(() => useJobFilters());
    result.current.setFilters({ status: "all" });
    result.current.setFilters({});
    expect(nav.push).not.toHaveBeenCalled();
    expect(nav.replace).not.toHaveBeenCalled();
  });
});

describe("JobFilterBar", () => {
  test("selects and checkbox push history entries", () => {
    nav.query = "page=2";
    render(<JobFilterBar />);
    fireEvent.change(screen.getByLabelText("Status"), { target: { value: "closed" } });
    expect(nav.push).toHaveBeenLastCalledWith("/jobs?status=closed", { scroll: false });
    fireEvent.click(screen.getByLabelText("Remote only"));
    expect(nav.push).toHaveBeenLastCalledWith("/jobs?remote=1", { scroll: false });
    fireEvent.change(screen.getByLabelText("Sort"), { target: { value: "salary" } });
    expect(nav.push).toHaveBeenLastCalledWith("/jobs?sort=salary", { scroll: false });
    expect(screen.getAllByRole("option").map((o) => o.textContent)).toEqual(["Open", "Closed", "All", "Newest", "Highest salary"]);
  });

  test("search is instant locally and debounced into the URL with replace", () => {
    vi.useFakeTimers();
    render(<JobFilterBar />);
    const input = screen.getByLabelText("Search");
    fireEvent.change(input, { target: { value: "d" } });
    act(() => vi.advanceTimersByTime(200));
    fireEvent.change(input, { target: { value: "data" } });
    expect(input).toHaveValue("data");
    act(() => vi.advanceTimersByTime(299));
    expect(nav.replace).not.toHaveBeenCalled();
    act(() => vi.advanceTimersByTime(1));
    expect(nav.replace).toHaveBeenCalledTimes(1);
    expect(nav.replace).toHaveBeenCalledWith("/jobs?q=data", { scroll: false });
    expect(nav.push).not.toHaveBeenCalled();
  });

  test("adopts q when the URL changes from outside", () => {
    vi.useFakeTimers();
    nav.query = "q=data";
    const { rerender } = render(<JobFilterBar />);
    expect(screen.getByLabelText("Search")).toHaveValue("data");
    nav.query = "q=ai";
    rerender(<JobFilterBar />);
    expect(screen.getByLabelText("Search")).toHaveValue("ai");
    act(() => vi.advanceTimersByTime(500));
    expect(nav.replace).not.toHaveBeenCalled();
  });
});

test("types", () => {
  expect(typecheckFolder(import.meta.dirname).output).toBe("");
});

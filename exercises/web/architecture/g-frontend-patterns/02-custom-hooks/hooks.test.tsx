import { act, renderHook } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import { getPageItems, usePagination } from "./pagination";
import { useControllableState } from "./use-controllable-state";
import { useDisclosure } from "./use-disclosure";

describe("getPageItems", () => {
  test.each([
    [{ page: 1, totalPages: 1 }, [1]],
    [{ page: 1, totalPages: 0 }, []],
    [{ page: 5, totalPages: 10 }, [1, "…", 4, 5, 6, "…", 10]],
    [{ page: 3, totalPages: 10 }, [1, 2, 3, 4, "…", 10]],
    [{ page: 1, totalPages: 10 }, [1, 2, "…", 10]],
    [{ page: 10, totalPages: 10 }, [1, "…", 9, 10]],
    [{ page: 4, totalPages: 7 }, [1, 2, 3, 4, 5, 6, 7]],
    [{ page: 1, totalPages: 5, siblings: 2 }, [1, 2, 3, 4, 5]],
    [{ page: 6, totalPages: 12, siblings: 2 }, [1, "…", 4, 5, 6, 7, 8, "…", 12]],
    [{ page: 99, totalPages: 3 }, [1, 2, 3]],
    [{ page: -4, totalPages: 8 }, [1, 2, "…", 8]],
  ])("%o", (input, expected) => {
    expect(getPageItems(input)).toEqual(expected);
  });
});

describe("usePagination", () => {
  test("derives pages and navigates within range", () => {
    const onPageChange = vi.fn();
    const { result, rerender } = renderHook((page: number) => usePagination({ total: 95, pageSize: 20, page, onPageChange }), { initialProps: 1 });
    expect(result.current.totalPages).toBe(5);
    expect(result.current.items).toEqual([1, 2, "…", 5]);
    expect(result.current.hasPrevious).toBe(false);
    expect(result.current.hasNext).toBe(true);
    result.current.previous();
    expect(onPageChange).not.toHaveBeenCalled();
    result.current.next();
    expect(onPageChange).toHaveBeenLastCalledWith(2);
    result.current.goTo(99);
    expect(onPageChange).toHaveBeenLastCalledWith(5);
    rerender(5);
    expect(result.current.hasNext).toBe(false);
    result.current.goTo(5);
    result.current.next();
    expect(onPageChange).toHaveBeenCalledTimes(2);
  });

  test("no results", () => {
    const { result } = renderHook(() => usePagination({ total: 0, pageSize: 20, page: 1, onPageChange: vi.fn() }));
    expect(result.current).toMatchObject({ totalPages: 0, items: [], hasPrevious: false, hasNext: false });
  });
});

test("useDisclosure with stable callbacks", () => {
  const { result, rerender } = renderHook(() => useDisclosure());
  const first = result.current;
  expect(first.isOpen).toBe(false);
  act(() => first.open());
  expect(result.current.isOpen).toBe(true);
  act(() => result.current.toggle());
  expect(result.current.isOpen).toBe(false);
  act(() => result.current.toggle());
  act(() => result.current.close());
  expect(result.current.isOpen).toBe(false);
  rerender();
  expect(result.current.open).toBe(first.open);
  expect(result.current.close).toBe(first.close);
  expect(result.current.toggle).toBe(first.toggle);
  expect(renderHook(() => useDisclosure(true)).result.current.isOpen).toBe(true);
});

describe("useControllableState", () => {
  test("uncontrolled", () => {
    const onChange = vi.fn();
    const { result } = renderHook(() => useControllableState({ defaultValue: "saved", onChange }));
    expect(result.current[0]).toBe("saved");
    act(() => result.current[1]("applied"));
    expect(result.current[0]).toBe("applied");
    expect(onChange).toHaveBeenCalledWith("applied");
    act(() => result.current[1]("applied"));
    expect(onChange).toHaveBeenCalledTimes(1);
  });

  test("controlled", () => {
    const onChange = vi.fn();
    const { result, rerender } = renderHook(({ value }) => useControllableState({ value, defaultValue: 0, onChange }), { initialProps: { value: 3 } });
    expect(result.current[0]).toBe(3);
    act(() => result.current[1]((prev) => prev + 1));
    expect(onChange).toHaveBeenCalledWith(4);
    expect(result.current[0]).toBe(3);
    rerender({ value: 4 });
    expect(result.current[0]).toBe(4);
    act(() => result.current[1](4));
    expect(onChange).toHaveBeenCalledTimes(1);
  });

  test("setValue is stable even with inline onChange", () => {
    const calls: number[] = [];
    const { result, rerender } = renderHook(({ tag }) => useControllableState({ defaultValue: 1, onChange: (v) => calls.push(v * tag) }), { initialProps: { tag: 1 } });
    const setValue = result.current[1];
    rerender({ tag: 10 });
    expect(result.current[1]).toBe(setValue);
    act(() => result.current[1](2));
    expect(calls).toEqual([20]);
  });
});

test("types", () => {
  expect(typecheckFolder(import.meta.dirname).output).toBe("");
});

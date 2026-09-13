import { readFileSync } from "node:fs";
import { join } from "node:path";
import { afterEach, describe, expect, test, vi } from "vitest";
import { createCounter, debounce, isBlank, salaryLabel, slugify } from "./basics.js";

describe("slugify", () => {
  test.each([
    ["  Senior Backend Engineer (Python) ", "senior-backend-engineer-python"],
    ["AI/ML Engineer", "ai-ml-engineer"],
    ["---Hello---World---", "hello-world"],
    ["C++ & C# Dev 2026", "c-c-dev-2026"],
    ["", ""],
  ])("%j → %j", (input, expected) => {
    expect(slugify(input)).toBe(expected);
  });
});

describe("salaryLabel", () => {
  test.each([
    [9_000_000, 14_000_000, "Rp 9–14 juta"],
    [null, 14_000_000, "Up to Rp 14 juta"],
    [9_000_000, undefined, "From Rp 9 juta"],
    [null, null, "Not disclosed"],
    [10_000_000, 10_000_000, "Rp 10 juta"],
    [9_500_000, 12_250_000, "Rp 9.5–12.3 juta"],
    [0, 5_000_000, "Rp 0–5 juta"],
  ])("(%j, %j) → %j", (min, max, expected) => {
    expect(salaryLabel(min, max)).toBe(expected);
  });

  test("min above max is a RangeError", () => {
    expect(() => salaryLabel(15_000_000, 9_000_000)).toThrow(RangeError);
  });
});

describe("isBlank", () => {
  test.each([
    [null, true],
    [undefined, true],
    ["", true],
    ["   \n", true],
    ["a", false],
    [0, false],
    [false, false],
    [[], false],
    [NaN, false],
  ])("%j → %j", (value, expected) => {
    expect(isBlank(value)).toBe(expected);
  });
});

test("createCounter keeps private state per counter", () => {
  const a = createCounter(5);
  const b = createCounter();
  a.increment();
  a.increment();
  b.decrement();
  expect(a.value()).toBe(7);
  expect(b.value()).toBe(-1);
  a.reset();
  expect(a.value()).toBe(5);
  expect(Object.keys(a).sort()).toEqual(["decrement", "increment", "reset", "value"]);
  expect("count" in a).toBe(false);
});

describe("debounce", () => {
  afterEach(() => vi.useRealTimers());

  test("calls once with the latest arguments after the wait", () => {
    vi.useFakeTimers();
    const search = vi.fn();
    const debounced = debounce(search, 300);
    debounced("p");
    vi.advanceTimersByTime(200);
    debounced("py");
    vi.advanceTimersByTime(200);
    debounced("pyt");
    expect(search).not.toHaveBeenCalled();
    vi.advanceTimersByTime(300);
    expect(search).toHaveBeenCalledTimes(1);
    expect(search).toHaveBeenCalledWith("pyt");
    debounced("python");
    vi.advanceTimersByTime(300);
    expect(search).toHaveBeenLastCalledWith("python");
  });
});

test("modern syntax: no var, no loose equality", () => {
  const source = readFileSync(join(import.meta.dirname, "basics.js"), "utf8").replace(/\/\/.*$|\/\*[\s\S]*?\*\//gm, "");
  expect(source).not.toMatch(/\bvar\s/);
  expect(source).not.toMatch(/[^=!]==[^=]|!=[^=]/);
});

import { describe, expect, test } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import { formatAmount, midpoint, parseRange, parseSalary } from "./salary";

describe("behavior", () => {
  test.each([
    ["Rp 12.000.000", 12_000_000],
    ["12000000", 12_000_000],
    ["$1,500", 1_500],
    ["Negotiable", null],
    ["", null],
  ])("parseSalary(%j) → %j", (input, expected) => {
    expect(parseSalary(input)).toBe(expected);
  });

  test.each([
    ["Rp 9.000.000 - Rp 14.000.000", [9_000_000, 14_000_000]],
    ["Rp 9.000.000–Rp 14.000.000", [9_000_000, 14_000_000]],
    ["Up to Rp 14.000.000", [14_000_000, 14_000_000]],
    ["Competitive", [null, null]],
  ])("parseRange(%j)", (input, expected) => {
    expect(parseRange(input)).toEqual(expected);
  });

  test("formatAmount", () => {
    expect(formatAmount(12_000_000)).toBe("Rp 12.000.000");
    expect(formatAmount(999)).toBe("Rp 999");
    expect(formatAmount(1_500, "USD")).toBe("$1,500");
    expect(formatAmount(1_234_567.6, "USD")).toBe("$1,234,568");
  });

  test("midpoint", () => {
    expect(midpoint([9_000_000, 14_000_001])).toBe(11_500_000);
    expect(midpoint([null, 14_000_000])).toBeNull();
  });
});

test("tsc passes in strict mode (including the @ts-expect-error checks)", () => {
  const result = typecheckFolder(import.meta.dirname);
  expect(result.output).toBe("");
  expect(result.ok).toBe(true);
});

test("no any and no ts-nocheck", async () => {
  const { readFileSync } = await import("node:fs");
  const source = readFileSync(`${import.meta.dirname}/salary.ts`, "utf8");
  expect(source).not.toMatch(/@ts-nocheck|@ts-ignore|:\s*any\b|as any\b|<any>/);
});

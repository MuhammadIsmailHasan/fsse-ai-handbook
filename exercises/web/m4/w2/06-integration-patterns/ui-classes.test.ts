import { readFileSync } from "node:fs";
import { describe, expect, test } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import { STATUS_BADGE, badgeClasses, buttonClasses, cn } from "./ui-classes";

const tokens = (classes: string) => classes.split(" ");

describe("cn", () => {
  test("conditional classes and conflict resolution", () => {
    expect(cn("px-4", false && "hidden", null, undefined, { "font-bold": true, italic: false }, ["mt-2"])).toBe("px-4 font-bold mt-2");
    expect(cn("px-4 py-2", "px-8")).toBe("py-2 px-8");
    expect(cn("bg-indigo-600 hover:bg-indigo-500", "bg-red-600")).toBe("hover:bg-indigo-500 bg-red-600");
  });
});

describe("buttonClasses", () => {
  test("defaults", () => {
    expect(buttonClasses()).toBe(
      "inline-flex items-center justify-center rounded-lg font-semibold focus-visible:outline-2 focus-visible:outline-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-indigo-600 text-white hover:bg-indigo-500 px-4 py-2 text-sm",
    );
  });

  test("variants, sizes and full width", () => {
    const danger = tokens(buttonClasses({ variant: "danger", size: "lg", fullWidth: true }));
    expect(danger).toEqual(expect.arrayContaining(["bg-red-600", "px-5", "py-3", "text-base", "w-full"]));
    expect(danger).not.toContain("bg-indigo-600");
    expect(tokens(buttonClasses({ variant: "secondary", size: "sm" }))).toEqual(expect.arrayContaining(["ring-1", "ring-slate-300", "px-2.5"]));
    expect(tokens(buttonClasses({ fullWidth: false }))).not.toContain("w-full");
  });

  test("className overrides conflicting utilities", () => {
    const result = tokens(buttonClasses({ className: "px-8 rounded-full" }));
    expect(result).toContain("px-8");
    expect(result).not.toContain("px-4");
    expect(result).toContain("rounded-full");
    expect(result).not.toContain("rounded-lg");
  });
});

describe("badges", () => {
  test("every status has background and text colors", () => {
    for (const [status, value] of Object.entries(STATUS_BADGE)) {
      expect(value, status).toMatch(/\bbg-\S+/);
      expect(value, status).toMatch(/\btext-\S+/);
    }
  });

  test("badgeClasses merges", () => {
    const offer = tokens(badgeClasses("offer", "px-3"));
    expect(offer).toEqual(expect.arrayContaining(["inline-flex", "rounded-full", "px-3", ...tokens(STATUS_BADGE.offer)]));
    expect(offer).not.toContain("px-2");
  });
});

test("types: satisfies and tsc strict", () => {
  const source = readFileSync(`${import.meta.dirname}/ui-classes.ts`, "utf8");
  expect(source.match(/satisfies Record</g)?.length).toBeGreaterThanOrEqual(3);
  expect(typecheckFolder(import.meta.dirname).output).toBe("");
});

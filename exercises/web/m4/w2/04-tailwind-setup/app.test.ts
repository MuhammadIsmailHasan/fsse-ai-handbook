// @vitest-environment node
import { beforeAll, describe, expect, test } from "vitest";
import { compileTailwind } from "@support/tailwind";

let css = "";
beforeAll(async () => {
  css = await compileTailwind(`${import.meta.dirname}/app.css`);
}, 30_000);

const ruleFor = (selector: string) => {
  const start = css.indexOf(selector);
  return start === -1 ? "" : css.slice(start, css.indexOf("}", start) + 1);
};

describe("generated utilities", () => {
  test("Tailwind is imported and the HTML is scanned", () => {
    expect(css).toContain(".grid");
    expect(css).toContain(".rounded-xl");
    expect(css).toContain(".sm\\:grid-cols-2");
  });

  test("brand colors from @theme", () => {
    expect(css).toMatch(/--color-brand-500:/);
    expect(ruleFor(".bg-brand-500")).toContain("var(--color-brand-500)");
    expect(ruleFor(".text-brand-50")).toContain("var(--color-brand-50)");
    expect(css).toMatch(/\.hover\\:bg-brand-600:hover/);
  });

  test("display font token", () => {
    expect(css).toMatch(/--font-display:\s*"Plus Jakarta Sans"/);
    expect(ruleFor(".font-display")).toContain("var(--font-display)");
  });

  test("custom 3xl breakpoint", () => {
    expect(css).toMatch(/@media \(width >= 120rem\)\s*{\s*\.\\33xl\\:grid-cols-4|\.\\33 xl\\:grid-cols-4/);
  });

  test("class-based dark mode", () => {
    expect(css).toMatch(/\.dark\\:bg-slate-900:where\(\.dark, \.dark \*\)/);
  });

  test("custom utility", () => {
    const rule = ruleFor(".container-page");
    expect(rule).toContain("max-width: 72rem");
    expect(rule).toContain("margin-inline: auto");
    expect(rule).toContain("padding-inline: 1rem");
  });

  test("base body styles", () => {
    expect(css).toMatch(/body\s*{\s*background-color: var\(--color-slate-50\);\s*color: var\(--color-slate-900\);/);
  });
});

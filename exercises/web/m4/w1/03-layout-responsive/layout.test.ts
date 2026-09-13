import { readFileSync } from "node:fs";
import { join } from "node:path";
import { declarationsFor, parseCss } from "@support/css";
import { describe, expect, test } from "vitest";

const rules = parseCss(readFileSync(join(import.meta.dirname, "layout.css"), "utf8"));
const decl = (selector: string, media: string | null = null) => declarationsFor(rules, selector, media);

describe("base (mobile) layout", () => {
  test("centered container", () => {
    const container = decl(".container");
    expect(container["max-width"]).toMatch(/rem$/);
    expect(container["margin-inline"] ?? `${container["margin-left"]} ${container["margin-right"]}`).toMatch(/auto/);
    expect(Object.keys(container).some((p) => p.startsWith("padding"))).toBe(true);
  });

  test("header is a wrapping flex row", () => {
    const header = decl(".site-header");
    expect(header).toMatchObject({ display: "flex", "justify-content": "space-between", "align-items": "center", "flex-wrap": "wrap" });
    expect(header["gap"]).toBeTruthy();
  });

  test("page is a one-column grid on phones", () => {
    const page = decl(".page");
    expect(page["display"]).toBe("grid");
    expect(page["gap"]).toBeTruthy();
    expect(page["grid-template-columns"], "no columns in the base rule — add them in a media query").toBeUndefined();
  });

  test("job list uses auto-fill with minmax", () => {
    const jobs = decl(".jobs");
    expect(jobs["display"]).toBe("grid");
    expect(jobs["gap"]).toBeTruthy();
    expect(jobs["grid-template-columns"]?.replace(/\s/g, "")).toMatch(/^repeat\(auto-(fill|fit),minmax\([\d.]+rem,1fr\)\)$/);
  });

  test("fluid images", () => {
    expect(decl("img")).toMatchObject({ "max-width": "100%", height: "auto" });
  });
});

describe("larger screens", () => {
  test("mobile-first media queries in em/rem", () => {
    const media = [...new Set(rules.map((r) => r.media).filter(Boolean))];
    expect(media.length).toBeGreaterThan(0);
    for (const query of media) expect(query).toMatch(/min-width:\s*[\d.]+(em|rem)/);
  });

  test("two columns from 48rem", () => {
    const page = decl(".page", "(min-width: 48rem)");
    expect(page["grid-template-columns"]?.split(/\s+/)).toHaveLength(2);
    expect(page["grid-template-columns"]).toMatch(/1fr$/);
  });

  test("no fixed pixel widths", () => {
    const offenders = rules.filter((r) => /px/.test(r.declarations["width"] ?? "") || /px/.test(r.declarations["min-width"] ?? ""));
    expect(offenders.map((r) => r.selector)).toEqual([]);
  });
});

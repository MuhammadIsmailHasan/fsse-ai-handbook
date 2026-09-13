import { readFileSync } from "node:fs";
import { join } from "node:path";
import { declarationsFor, parseCss, rulesFor } from "@support/css";
import { describe, expect, test } from "vitest";

const css = readFileSync(join(import.meta.dirname, "styles.css"), "utf8");
const rules = parseCss(css);
const decl = (selector: string) => declarationsFor(rules, selector);

describe("tokens and base", () => {
  test("design tokens on :root", () => {
    const root = decl(":root");
    for (const token of ["--color-primary", "--color-text", "--color-muted", "--color-surface", "--radius", "--space-1", "--space-2", "--space-4"]) {
      expect(root[token], token).toBeTruthy();
    }
  });

  test("border-box reset for everything", () => {
    const reset = rules.find((r) => ["*", "*::before", "*::after"].every((s) => r.selector.split(",").map((x) => x.trim()).includes(s)));
    expect(reset?.declarations["box-sizing"]).toBe("border-box");
  });

  test("body typography", () => {
    const body = decl("body");
    expect(body["font-family"]).toMatch(/,/);
    expect(body["font-family"]).toMatch(/(sans-serif|system-ui|serif)\s*$/);
    expect(body["line-height"]).toMatch(/^\d+(\.\d+)?$/);
    expect(body["color"]).toBe("var(--color-text)");
  });
});

describe("components", () => {
  test("card uses tokens", () => {
    const card = decl(".card");
    expect(card["background"] ?? card["background-color"]).toContain("var(--color-surface)");
    expect(card["padding"]).toMatch(/var\(--space-\d\)/);
    expect(card["border-radius"]).toBe("var(--radius)");
  });

  test("title in rem and muted meta", () => {
    expect(decl(".card__title")["font-size"]).toMatch(/rem$/);
    expect(decl(".card__meta")["color"]).toBe("var(--color-muted)");
  });

  test("badge block and modifier", () => {
    const badge = decl(".badge");
    expect(badge["display"]).toBe("inline-block");
    expect(Object.keys(badge).some((p) => p.startsWith("padding"))).toBe(true);
    const remote = decl(".badge--remote");
    expect(remote["background"] ?? remote["background-color"]).toContain("var(--color-primary)");
  });

  test("hover and keyboard focus states", () => {
    expect(rulesFor(rules, ".button:hover").length).toBeGreaterThan(0);
    const focus = decl(".button:focus-visible");
    expect(focus["outline"]).toBeTruthy();
    expect(focus["outline"]).not.toMatch(/^(none|0)/);
  });
});

describe("hygiene", () => {
  test("no id selectors, !important or px font sizes", () => {
    expect(rules.filter((r) => /#[\w-]/.test(r.selector)).map((r) => r.selector)).toEqual([]);
    expect(rules.flatMap((r) => r.important)).toEqual([]);
    expect(rules.filter((r) => /px$/.test(r.declarations["font-size"] ?? "")).map((r) => r.selector)).toEqual([]);
  });

  test("the stylesheet is not empty", () => {
    expect(rules.length).toBeGreaterThanOrEqual(8);
  });
});

// @vitest-environment node
import { readFileSync } from "node:fs";
import { JSDOM } from "jsdom";
import { beforeAll, describe, expect, test } from "vitest";
import { compileTailwind } from "@support/tailwind";

const html = readFileSync(`${import.meta.dirname}/job-list.html`, "utf8");
const doc = new JSDOM(html).window.document;
let css = "";

beforeAll(async () => {
  css = await compileTailwind(`${import.meta.dirname}/app.css`);
}, 30_000);

const classes = (el: Element | null) => new Set((el?.getAttribute("class") ?? "").split(/\s+/).filter(Boolean));
const expectClasses = (el: Element | null, required: string[]) => {
  const set = classes(el);
  expect(required.filter((c) => !set.has(c)), `missing on <${el?.tagName.toLowerCase()}>`).toEqual([]);
};

describe("layout", () => {
  test("container, heading and grid", () => {
    const main = doc.querySelector("main");
    expectClasses(main, ["mx-auto", "px-4"]);
    expect([...classes(main)].some((c) => /^max-w-(4xl|5xl|6xl)$/.test(c))).toBe(true);
    const h1 = doc.querySelector("h1");
    expectClasses(h1, ["text-2xl", "font-bold", "tracking-tight"]);
    expect([...classes(h1)].some((c) => /^sm:text-(3xl|4xl)$/.test(c))).toBe(true);
    const ul = doc.querySelector("ul");
    expectClasses(ul, ["grid", "sm:grid-cols-2", "lg:grid-cols-3"]);
    expect([...classes(ul)].some((c) => /^gap-\d+$/.test(c))).toBe(true);
  });
});

describe("cards", () => {
  test("every card, title, description, badge and button", () => {
    const cards = [...doc.querySelectorAll("article")];
    expect(cards).toHaveLength(3);
    for (const card of cards) {
      expectClasses(card, ["rounded-xl", "border", "border-slate-200", "bg-white", "p-4", "shadow-sm", "dark:border-slate-800", "dark:bg-slate-900", "flex", "flex-col"]);
      expectClasses(card.querySelector("h2"), ["text-lg", "font-semibold"]);
      expectClasses(card.querySelector("p"), ["line-clamp-2", "text-sm", "text-slate-600", "dark:text-slate-300"]);
      expectClasses(card.querySelector("span"), ["inline-flex", "items-center", "rounded-full", "px-2", "py-0.5", "text-xs", "font-medium"]);
      expectClasses(card.querySelector("button"), [
        "mt-auto", "rounded-lg", "bg-indigo-600", "px-4", "py-2", "text-white", "hover:bg-indigo-500",
        "focus-visible:outline-2", "focus-visible:outline-offset-2", "focus-visible:outline-indigo-600", "disabled:opacity-50",
      ]);
    }
  });
});

describe("utility hygiene", () => {
  test("no inline styles or arbitrary values", () => {
    expect(doc.querySelectorAll("[style]")).toHaveLength(0);
    const all = [...doc.querySelectorAll("[class]")].flatMap((el) => [...classes(el)]);
    expect(all.filter((c) => c.includes("["))).toEqual([]);
  });

  test("every class generates CSS (no typos)", () => {
    const all = new Set([...doc.querySelectorAll("[class]")].flatMap((el) => [...classes(el)]));
    const escape = (c: string) => c.replace(/[:.\/]/g, (m) => `\\${m}`);
    const unknown = [...all].filter((c) => !css.includes(`.${escape(c)}`));
    expect(unknown).toEqual([]);
    expect(css).toContain("@media (width >= 40rem)");
    expect(css).toContain("@media (width >= 64rem)");
  });
});

import { readFileSync } from "node:fs";
import { join } from "node:path";
import { JSDOM } from "jsdom";
import { beforeAll, describe, expect, test } from "vitest";

const source = readFileSync(join(import.meta.dirname, "job.html"), "utf8");
let doc: Document;

beforeAll(() => {
  doc = new JSDOM(source).window.document;
});

const all = (selector: string) => [...doc.querySelectorAll(selector)];

describe("document basics", () => {
  test("doctype, language, charset, viewport and title", () => {
    expect(source.trimStart().toLowerCase().startsWith("<!doctype html>")).toBe(true);
    expect(doc.documentElement.getAttribute("lang")).toBe("en");
    expect(doc.querySelector("meta[charset]")?.getAttribute("charset")?.toLowerCase()).toBe("utf-8");
    expect(doc.querySelector('meta[name="viewport"]')?.getAttribute("content")).toContain("width=device-width");
    expect(doc.title.trim().length).toBeGreaterThan(0);
  });
});

describe("landmarks and headings", () => {
  test("header, nav, main and footer", () => {
    for (const tag of ["header", "main", "footer"]) {
      expect(all(`body > ${tag}`), `<${tag}> directly inside <body>`).toHaveLength(1);
    }
    expect(all("nav")).toHaveLength(1);
    expect(all("nav a").length).toBeGreaterThanOrEqual(2);
  });

  test("one h1 and no skipped heading levels", () => {
    const h1s = all("h1");
    expect(h1s).toHaveLength(1);
    expect(h1s[0]!.textContent?.trim()).toBe("Backend Engineer");
    const levels = all("h1, h2, h3, h4, h5, h6").map((h) => Number(h.tagName[1]));
    levels.forEach((level, i) => {
      if (i > 0) expect(level - levels[i - 1]!, "heading levels must not skip").toBeLessThanOrEqual(1);
    });
  });

  test("article with sections", () => {
    const article = doc.querySelector("main article");
    expect(article).not.toBeNull();
    const titles = [...article!.querySelectorAll("section")].map((s) => s.firstElementChild);
    expect(titles.map((t) => t?.tagName)).toEqual(["H2", "H2"]);
    expect(titles.map((t) => t?.textContent?.trim())).toEqual(["Requirements", "Apply"]);
  });
});

describe("meaningful content elements", () => {
  test("skills list, salary data and posted time", () => {
    expect(all("section ul > li").map((li) => li.textContent?.trim())).toEqual(["Python", "PostgreSQL", "Docker"]);
    expect(doc.querySelector('data[value="14000000"]')).not.toBeNull();
    expect(doc.querySelector('time[datetime="2026-09-01"]')).not.toBeNull();
  });

  test("image alt text and descriptive links", () => {
    for (const img of all("img")) {
      const alt = img.getAttribute("alt");
      expect(alt, "every image needs alt text").toBeTruthy();
      expect(alt!.toLowerCase()).not.toMatch(/^(image|logo|picture)$/);
    }
    for (const link of all("a")) {
      expect(link.getAttribute("href")).toBeTruthy();
      expect(link.textContent?.trim().toLowerCase()).not.toMatch(/^(here|click here|link)$/);
    }
  });
});

describe("accessible form", () => {
  test("labels, types and a real submit button", () => {
    const form = doc.querySelector("form");
    expect(form).not.toBeNull();
    const fields = [...form!.querySelectorAll("input, textarea")];
    expect(fields.length).toBeGreaterThanOrEqual(3);
    for (const field of fields) {
      const id = field.getAttribute("id");
      expect(id, "fields need an id").toBeTruthy();
      expect(form!.querySelector(`label[for="${id}"]`), `label for #${id}`).not.toBeNull();
    }
    const email = form!.querySelector("#email");
    expect(email?.getAttribute("type")).toBe("email");
    expect(email?.hasAttribute("required")).toBe(true);
    expect(form!.querySelector('button[type="submit"]')?.textContent?.trim()).toBe("Send application");
  });

  test("no inline styles or inline event handlers", () => {
    expect(all("[style]")).toHaveLength(0);
    expect(all("[onclick]")).toHaveLength(0);
  });
});

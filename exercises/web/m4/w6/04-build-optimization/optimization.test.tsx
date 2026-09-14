import { render, screen } from "@testing-library/react";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";

vi.mock("server-only", () => ({}));

import nextConfig from "./next.config";
import { JobDescription } from "./components/job-description";
import { SalaryChartLazy } from "./components/salary-chart-lazy";

const dir = import.meta.dirname;
const read = (file: string) => readFileSync(join(dir, file), "utf8");
const withoutComments = (source: string) => source.replace(/\/\*[\s\S]*?\*\/|\{\/\*[\s\S]*?\*\/\}|\/\/.*$/gm, "");

function sourceFiles(folder = dir): string[] {
  return readdirSync(folder).flatMap((name) => {
    const full = join(folder, name);
    if (["solution", "node_modules"].includes(name)) return [];
    if (statSync(full).isDirectory()) return sourceFiles(full);
    return /\.tsx?$/.test(name) && !name.includes(".test.") ? [full] : [];
  });
}

describe("next.config.ts", () => {
  test("images and headers", () => {
    expect(nextConfig.poweredByHeader).toBe(false);
    expect(nextConfig.images?.formats).toEqual(["image/avif", "image/webp"]);
    const patterns = nextConfig.images?.remotePatterns ?? [];
    expect(patterns).toHaveLength(1);
    const pattern = patterns[0]!;
    const asUrl = pattern instanceof URL ? pattern : null;
    expect(asUrl?.href ?? `${(pattern as { protocol?: string }).protocol}://${(pattern as { hostname: string }).hostname}${(pattern as { pathname?: string }).pathname}`).toBe(
      "https://cdn.careerpilot.app/logos/**",
    );
  });
});

describe("fonts", () => {
  test("next/font instead of a render-blocking stylesheet", () => {
    const layout = withoutComments(read("app/layout.tsx"));
    expect(layout).not.toMatch(/fonts\.googleapis\.com|<link/);
    expect(layout).toMatch(/import\s*\{\s*Inter\s*\}\s*from\s*["']next\/font\/google["']/);
    expect(layout).toMatch(/Inter\(\{[^}]*subsets:\s*\[\s*["']latin["']\s*\]/);
    expect(layout).toMatch(/display:\s*["']swap["']/);
    expect(layout).toMatch(/variable:\s*["']--font-sans["']/);
    expect(layout).toMatch(/<html[^>]*className=\{\s*\w+\.variable\s*\}/);
  });
});

describe("job page", () => {
  const page = () => withoutComments(read("app/jobs/[id]/page.tsx"));

  test("uses next/image with dimensions, alt text and preload for the LCP image", () => {
    const source = page();
    expect(source).not.toMatch(/<img\b/);
    expect(source).toMatch(/import\s+Image\s+from\s+["']next\/image["']/);
    const images = [...source.matchAll(/<Image\b([\s\S]*?)\/>/g)].map((m) => m[1]!);
    expect(images).toHaveLength(2);
    const banner = images.find((attrs) => attrs.includes("bannerUrl"))!;
    const logo = images.find((attrs) => attrs.includes("logoUrl"))!;
    expect(banner).toMatch(/width=\{1200\}/);
    expect(banner).toMatch(/height=\{400\}/);
    expect(banner).toMatch(/sizes=["']100vw["']/);
    expect(banner).toMatch(/\bpreload\b/);
    expect(banner).toMatch(/alt=\{`\$\{job\.title\} at \$\{job\.company\}`\}/);
    expect(logo).toMatch(/width=\{64\}/);
    expect(logo).toMatch(/height=\{64\}/);
    expect(logo).toMatch(/alt=\{`\$\{job\.company\} logo`\}/);
    expect(source).not.toMatch(/\bpriority\b/);
  });

  test("renders the lazy chart and the server description", () => {
    const source = page();
    expect(source).toMatch(/<SalaryChartLazy\b/);
    expect(source).not.toMatch(/components\/salary-chart["']/);
    expect(source).toMatch(/<JobDescription\b/);
  });
});

describe("bundle boundaries", () => {
  test("no client file statically imports the heavy modules", () => {
    for (const file of sourceFiles()) {
      const source = withoutComments(readFileSync(file, "utf8"));
      if (!/^\s*["']use client["']/.test(source)) continue;
      const name = relative(dir, file);
      expect(source, `${name} imports the markdown parser`).not.toMatch(/from\s+["'][^"']*lib\/markdown["']/);
      if (name !== join("components", "salary-chart.tsx")) {
        expect(source, `${name} statically imports the chart`).not.toMatch(/from\s+["']\.{1,2}\/[^"']*salary-chart["']/);
      }
    }
  });

  test("JobDescription is a Server Component that renders markdown", () => {
    expect(read("components/job-description.tsx")).not.toMatch(/use client|useState/);
    const html = renderToStaticMarkup(<JobDescription markdown={"Build **reliable** pipelines.\n\n- Python\n- SQL"} />);
    expect(html).toBe('<div class="prose"><p>Build <strong>reliable</strong> pipelines.</p><ul><li>Python</li><li>SQL</li></ul></div>');
  });

  test("the chart is lazy, client-only and has a loading state", async () => {
    const source = withoutComments(read("components/salary-chart-lazy.tsx"));
    expect(source).toMatch(/^\s*["']use client["']/);
    expect(source).toMatch(/dynamic\(\s*\(\)\s*=>\s*import\(\s*["']\.\/salary-chart["']\s*\)/);
    expect(source).toMatch(/ssr:\s*false/);
    expect(renderToStaticMarkup(<SalaryChartLazy points={[{ label: "Mid", value: 1 }]} />)).not.toContain("Mid");
    render(<SalaryChartLazy points={[{ label: "Mid", value: 16_000_000 }]} />);
    expect(screen.getByText("Loading salary chart…")).toBeInTheDocument();
    expect(await screen.findByRole("figure", { name: "Salary chart" })).toHaveTextContent("Mid");
  });
});

test("types", () => {
  expect(typecheckFolder(dir, { recursive: true }).output).toBe("");
});

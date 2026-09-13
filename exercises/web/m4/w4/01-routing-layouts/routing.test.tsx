import { render, screen, within } from "@testing-library/react";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import { routeFromFile } from "./lib/routes";

vi.mock("next/navigation", () => ({
  notFound: vi.fn(() => {
    throw new Error("NEXT_NOT_FOUND");
  }),
}));

const here = (...parts: string[]) => join(import.meta.dirname, ...parts);
const load = async (path: string) => (await import(/* @vite-ignore */ here(path))).default;

describe("routeFromFile", () => {
  test.each([
    ["app/page.tsx", "/"],
    ["app/jobs/page.tsx", "/jobs"],
    ["app/jobs/[id]/page.tsx", "/jobs/[id]"],
    ["app/(auth)/login/page.tsx", "/login"],
    ["app/(marketing)/(legal)/terms/page.tsx", "/terms"],
    ["app/api/health/route.ts", "/api/health"],
    ["app/jobs/_components/row.tsx", null],
    ["app/_lib/page.tsx", null],
    ["app/layout.tsx", null],
    ["app/jobs/loading.tsx", null],
    ["src/page.tsx", null],
  ])("%s → %s", (file, expected) => {
    expect(routeFromFile(file)).toBe(expected);
  });
});

test("the route files exist with the right names", () => {
  for (const file of [
    "app/layout.tsx",
    "app/page.tsx",
    "app/jobs/page.tsx",
    "app/jobs/[id]/page.tsx",
    "app/jobs/[id]/loading.tsx",
    "app/jobs/[id]/not-found.tsx",
    "app/(auth)/login/page.tsx",
    "app/dashboard/layout.tsx",
    "app/dashboard/page.tsx",
  ]) {
    expect(existsSync(here(file)), file).toBe(true);
  }
});

test("root layout renders html, nav links and main", async () => {
  const RootLayout = await load("app/layout.tsx");
  const html = renderToStaticMarkup(<RootLayout><p>child</p></RootLayout>);
  expect(html).toMatch(/^<html lang="en">(<head><\/head>)?<body>/);
  const doc = new DOMParser().parseFromString(html, "text/html");
  const nav = doc.querySelector('header nav[aria-label="Main"]');
  expect([...(nav?.querySelectorAll("a") ?? [])].map((a) => [a.textContent, a.getAttribute("href")])).toEqual([
    ["Jobs", "/jobs"],
    ["Dashboard", "/dashboard"],
  ]);
  expect(doc.querySelector("main")?.innerHTML).toBe("<p>child</p>");
});

test("home and login pages", async () => {
  const Home = await load("app/page.tsx");
  const Login = await load("app/(auth)/login/page.tsx");
  render(
    <>
      <Home />
      <Login />
    </>,
  );
  expect(screen.getByRole("heading", { level: 1, name: "CareerPilot" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { level: 1, name: "Log in" })).toBeInTheDocument();
});

test("jobs page is an async server component with links", async () => {
  const JobsPage = await load("app/jobs/page.tsx");
  render(await JobsPage());
  expect(screen.getByRole("heading", { level: 1, name: "Jobs" })).toBeInTheDocument();
  expect(screen.getAllByRole("link").map((a) => [a.textContent, a.getAttribute("href")])).toEqual([
    ["Backend Engineer · Kopi Data", "/jobs/1"],
    ["AI Engineer · Lintas AI", "/jobs/2"],
  ]);
});

describe("dynamic job page", () => {
  test("renders a job from awaited params", async () => {
    const JobPage = await load("app/jobs/[id]/page.tsx");
    render(await JobPage({ params: Promise.resolve({ id: "2" }) }));
    expect(screen.getByRole("heading", { level: 1, name: "AI Engineer" })).toBeInTheDocument();
    expect(screen.getByText("Lintas AI · Remote")).toBeInTheDocument();
  });

  test.each(["99", "abc", "0", "1.5", "-1"])("id %j → notFound()", async (id) => {
    const JobPage = await load("app/jobs/[id]/page.tsx");
    await expect(JobPage({ params: Promise.resolve({ id }) })).rejects.toThrow("NEXT_NOT_FOUND");
  });

  test("loading and not-found UI", async () => {
    const Loading = await load("app/jobs/[id]/loading.tsx");
    const NotFound = await load("app/jobs/[id]/not-found.tsx");
    render(
      <>
        <Loading />
        <NotFound />
      </>,
    );
    expect(screen.getByRole("status")).toHaveTextContent("Loading job…");
    expect(screen.getByRole("heading", { name: "Job not found" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Back to jobs" })).toHaveAttribute("href", "/jobs");
  });
});

test("nested dashboard layout wraps the page", async () => {
  const DashboardLayout = await load("app/dashboard/layout.tsx");
  const DashboardPage = await load("app/dashboard/page.tsx");
  render(
    <DashboardLayout>
      <DashboardPage />
    </DashboardLayout>,
  );
  const aside = screen.getByRole("complementary", { name: "Dashboard" });
  expect(within(aside).getAllByRole("link").map((a) => a.getAttribute("href"))).toEqual(["/dashboard", "/dashboard/applications"]);
  expect(screen.getByRole("heading", { level: 1, name: "Dashboard" }).closest("section")).not.toBeNull();
});

test("all route files type-check", () => {
  expect(typecheckFolder(import.meta.dirname, { recursive: true }).output).toBe("");
});

import { render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import { EmptyState, JobCard, JobList, JobsPage, PageHeader, type Job } from "./job-components";

const JOBS: Job[] = [
  { id: 1, title: "Backend Engineer", company: "Kopi Data", city: "Jakarta", salaryMax: 14_000_000, skills: ["Python", "PostgreSQL"] },
  { id: 2, title: "AI Engineer", company: "Lintas AI", city: "Remote", salaryMax: null, skills: ["Python"] },
];

let consoleError: ReturnType<typeof vi.spyOn>;
beforeEach(() => {
  consoleError = vi.spyOn(console, "error");
});
afterEach(() => {
  const keyWarnings = consoleError.mock.calls.filter((args) => String(args[0]).includes("key"));
  expect(keyWarnings, "React warned about keys").toEqual([]);
});

test("PageHeader with and without subtitle", () => {
  const { rerender } = render(<PageHeader title="Jobs" subtitle="2 open positions" />);
  expect(screen.getByRole("banner")).toContainElement(screen.getByRole("heading", { level: 1, name: "Jobs" }));
  expect(screen.getByText("2 open positions")).toBeInTheDocument();
  rerender(<PageHeader title="Jobs" />);
  expect(screen.getByRole("banner").querySelectorAll("p")).toHaveLength(0);
});

test("JobCard shows details and optional salary", () => {
  const { rerender } = render(<JobCard job={JOBS[0]!} />);
  const card = screen.getByRole("article");
  expect(within(card).getByRole("heading", { level: 2, name: "Backend Engineer" })).toBeInTheDocument();
  expect(within(card).getByText("Kopi Data · Jakarta")).toBeInTheDocument();
  expect(within(within(card).getByRole("list", { name: "Skills" })).getAllByRole("listitem").map((li) => li.textContent)).toEqual(["Python", "PostgreSQL"]);
  expect(within(card).getByText("Up to Rp 14.000.000")).toBeInTheDocument();
  rerender(<JobCard job={JOBS[1]!} />);
  expect(screen.queryByText(/Up to Rp/)).toBeNull();
});

test("JobList renders cards or an empty state", () => {
  const { rerender } = render(<JobList jobs={JOBS} />);
  const items = screen.getAllByRole("listitem").filter((li) => li.querySelector("article"));
  expect(items).toHaveLength(2);
  rerender(<JobList jobs={[]} />);
  expect(screen.getByRole("status")).toHaveTextContent("No jobs yet");
  expect(screen.queryByRole("article")).toBeNull();
});

test("EmptyState renders children", () => {
  render(
    <EmptyState message="Nothing saved">
      <button type="button">Browse jobs</button>
    </EmptyState>,
  );
  expect(within(screen.getByRole("status")).getByRole("button", { name: "Browse jobs" })).toBeInTheDocument();
});

test("JobsPage composes everything", () => {
  render(<JobsPage jobs={JOBS} />);
  expect(screen.getByRole("heading", { level: 1, name: "Jobs for you" })).toBeInTheDocument();
  expect(screen.getByText("2 open positions")).toBeInTheDocument();
  expect(within(screen.getByRole("main")).getAllByRole("article")).toHaveLength(2);
});

test("types compile (strict, no any)", () => {
  expect(typecheckFolder(import.meta.dirname).output).toBe("");
});

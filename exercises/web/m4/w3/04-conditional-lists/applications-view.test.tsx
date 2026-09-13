import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import { ApplicationsView, type Application } from "./applications-view";

const APPS: Application[] = [
  { id: 7, role: "Backend Engineer", company: "Kopi Data", status: "interview", unread: 2 },
  { id: 3, role: "AI Engineer", company: "Lintas AI", status: "saved", unread: 0 },
  { id: 9, role: "Data Analyst", company: "Awan", status: "interview", unread: 0 },
  { id: 4, role: "QA", company: "Batik", status: "rejected", unread: 1 },
];

let consoleError: ReturnType<typeof vi.spyOn>;
beforeEach(() => {
  consoleError = vi.spyOn(console, "error");
});
afterEach(() => {
  expect(consoleError.mock.calls.filter((a) => String(a[0]).includes("key"))).toEqual([]);
});

test("idle renders nothing", () => {
  const { container } = render(<ApplicationsView state={{ status: "idle" }} onRetry={() => {}} />);
  expect(container).toBeEmptyDOMElement();
});

test("loading state", () => {
  render(<ApplicationsView state={{ status: "loading" }} onRetry={() => {}} />);
  expect(screen.getByRole("status")).toHaveTextContent("Loading applications…");
});

test("error state with retry", async () => {
  const onRetry = vi.fn();
  render(<ApplicationsView state={{ status: "error", message: "Couldn't reach the API" }} onRetry={onRetry} />);
  const alert = screen.getByRole("alert");
  expect(alert).toHaveTextContent("Couldn't reach the API");
  await userEvent.setup().click(within(alert).getByRole("button", { name: "Try again" }));
  expect(onRetry).toHaveBeenCalledTimes(1);
});

test("empty success", () => {
  render(<ApplicationsView state={{ status: "success", data: [] }} onRetry={() => {}} />);
  expect(screen.getByText("No applications yet")).toBeInTheDocument();
  expect(screen.queryByRole("group")).toBeNull();
});

test("groups in status order with correct items and no stray zeros", () => {
  const { container } = render(<ApplicationsView state={{ status: "success", data: APPS }} onRetry={() => {}} />);
  const sections = screen.getAllByRole("region");
  expect(sections.map((s) => within(s).getByRole("heading", { level: 2 }).textContent)).toEqual(["Saved", "Interview", "Rejected"]);
  const interview = screen.getByRole("region", { name: "Interview" });
  expect(within(interview).getAllByRole("listitem").map((li) => li.textContent)).toEqual(["Backend Engineer at Kopi Data 2 new", "Data Analyst at Awan"]);
  expect(within(screen.getByRole("region", { name: "Saved" })).getByRole("listitem").textContent).toBe("AI Engineer at Lintas AI");
  expect(container.textContent).not.toMatch(/Lintas AI0|Awan0/);
});

test("filter tabs", async () => {
  const user = userEvent.setup();
  render(<ApplicationsView state={{ status: "success", data: APPS }} onRetry={() => {}} />);
  const group = screen.getByRole("group", { name: "Filter by status" });
  expect(within(group).getAllByRole("button").map((b) => b.textContent)).toEqual(["All (4)", "Saved (1)", "Interview (2)", "Rejected (1)"]);
  expect(within(group).getByRole("button", { name: "All (4)" })).toHaveAttribute("aria-pressed", "true");
  await user.click(within(group).getByRole("button", { name: "Interview (2)" }));
  expect(screen.getAllByRole("region").map((s) => s.getAttribute("aria-label"))).toEqual(["Interview"]);
  expect(within(group).getByRole("button", { name: "Interview (2)" })).toHaveAttribute("aria-pressed", "true");
  expect(within(group).getByRole("button", { name: "All (4)" })).toHaveAttribute("aria-pressed", "false");
  await user.click(within(group).getByRole("button", { name: "All (4)" }));
  expect(screen.getAllByRole("region")).toHaveLength(3);
});

test("types compile", () => {
  expect(typecheckFolder(import.meta.dirname).output).toBe("");
});

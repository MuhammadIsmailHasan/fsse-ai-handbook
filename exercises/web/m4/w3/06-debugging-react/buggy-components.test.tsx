import { act, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { afterEach, expect, test, vi } from "vitest";
import { FiltersPanel, NotesEditor, ProfileHeader, SavedList, Stopwatch, type Filters } from "./buggy-components";

afterEach(() => vi.useRealTimers());

test("1 · SavedList shows a saved job immediately", async () => {
  const user = userEvent.setup();
  render(<SavedList />);
  await user.type(screen.getByLabelText("Job title"), "Backend Engineer");
  await user.click(screen.getByRole("button", { name: "Save" }));
  expect(within(screen.getByRole("list", { name: "Saved jobs" })).getAllByRole("listitem").map((li) => li.textContent)).toEqual(["Backend Engineer"]);
  await user.clear(screen.getByLabelText("Job title"));
  expect(within(screen.getByRole("list", { name: "Saved jobs" })).getAllByRole("listitem")).toHaveLength(1);
  await user.type(screen.getByLabelText("Job title"), "AI Engineer");
  await user.click(screen.getByRole("button", { name: "Save" }));
  expect(within(screen.getByRole("list", { name: "Saved jobs" })).getAllByRole("listitem")).toHaveLength(2);
});

test("2 · Stopwatch keeps counting and cleans up", () => {
  vi.useFakeTimers();
  const { unmount } = render(<Stopwatch />);
  act(() => vi.advanceTimersByTime(3000));
  expect(screen.getByText("Elapsed: 3s")).toBeInTheDocument();
  unmount();
  expect(vi.getTimerCount()).toBe(0);
});

test("3 · NotesEditor keeps the right text after deleting", async () => {
  const user = userEvent.setup();
  render(
    <NotesEditor
      initialNotes={[
        { id: "A", text: "Call recruiter" },
        { id: "B", text: "Send portfolio" },
        { id: "C", text: "Prepare questions" },
      ]}
    />,
  );
  await user.click(screen.getByRole("button", { name: "Delete A" }));
  expect(screen.getByLabelText("Note B")).toHaveValue("Send portfolio");
  expect(screen.getByLabelText("Note C")).toHaveValue("Prepare questions");
});

test("4 · FiltersPanel doesn't loop forever", async () => {
  const consoleError = vi.spyOn(console, "error").mockImplementation(() => {});
  let renders = 0;
  let changes = 0;
  function Page() {
    const [filters, setFilters] = useState<Filters | null>(null);
    renders++;
    // Safety valve: stop feeding the loop after 30 updates so a buggy version fails instead of freezing your computer.
    const onChange = (next: Filters) => {
      if (++changes <= 30) setFilters(next);
    };
    return (
      <>
        <FiltersPanel onChange={onChange} />
        <p>{filters ? `remote: ${filters.remote}` : "no filters"}</p>
      </>
    );
  }
  render(<Page />);
  expect(renders).toBeLessThan(10);
  expect(consoleError.mock.calls.filter((a) => String(a[0]).includes("Maximum update depth"))).toEqual([]);
  expect(screen.getByText("remote: false")).toBeInTheDocument();
  await userEvent.setup().click(screen.getByLabelText("Remote only"));
  expect(screen.getByText("remote: true")).toBeInTheDocument();
  expect(renders).toBeLessThan(15);
});

test("5 · ProfileHeader survives becoming an admin", async () => {
  vi.spyOn(console, "error").mockImplementation(() => {});
  const user = userEvent.setup();
  const siti = { name: "Siti", email: "siti@example.com", isAdmin: false };
  const { rerender } = render(<ProfileHeader user={siti} />);
  await user.click(screen.getByRole("button", { name: "Account menu" }));
  expect(screen.getByText("siti@example.com")).toBeInTheDocument();
  rerender(<ProfileHeader user={{ ...siti, isAdmin: true }} />);
  expect(screen.getByText("Hi, Siti (3 unread)")).toBeInTheDocument();
  expect(screen.getByText("siti@example.com")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "Admin view" }));
  expect(screen.getByRole("button", { name: "Admin view" })).toHaveAttribute("aria-pressed", "true");
});

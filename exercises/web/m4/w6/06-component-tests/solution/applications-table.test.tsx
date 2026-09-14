import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, test, vi } from "vitest";
import { ApplicationsTable, type ApplicationRow } from "./applications-table";

const APPLICATIONS: ApplicationRow[] = [
  { id: 11, role: "Backend Engineer", company: "Kopi Data", status: "applied", appliedOn: "2026-08-01" },
  { id: 12, role: "Data Engineer", company: "Nusantara Pay", status: "interview", appliedOn: "2026-08-20" },
  { id: 13, role: "Frontend Developer", company: "Batik Cloud", status: "offer", appliedOn: "2026-08-10" },
];

function setup(onDelete = vi.fn().mockResolvedValue(undefined)) {
  const user = userEvent.setup();
  render(<ApplicationsTable applications={APPLICATIONS} onDelete={onDelete} />);
  const roles = () => screen.queryAllByRole("row").slice(1).map((row) => within(row).getAllByRole("cell")[0]!.textContent);
  return { user, onDelete, roles };
}

describe("ApplicationsTable", () => {
  test("shows newest applications first with a count", () => {
    const { roles } = setup();
    expect(roles()).toEqual(["Data Engineer", "Frontend Developer", "Backend Engineer"]);
    expect(screen.getByRole("table", { name: "3 applications" })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Applied on" })).toHaveAttribute("aria-sort", "descending");
  });

  test("toggles the sort direction", async () => {
    const { user, roles } = setup();
    await user.click(screen.getByRole("button", { name: "Applied on" }));
    expect(roles()).toEqual(["Backend Engineer", "Frontend Developer", "Data Engineer"]);
    expect(screen.getByRole("columnheader", { name: "Applied on" })).toHaveAttribute("aria-sort", "ascending");
  });

  test("searches role and company, ignoring case", async () => {
    const { user, roles } = setup();
    await user.type(screen.getByLabelText("Search"), "  FRONTEND ");
    expect(roles()).toEqual(["Frontend Developer"]);
    expect(screen.getByRole("table", { name: "1 application" })).toBeInTheDocument();
    await user.clear(screen.getByLabelText("Search"));
    await user.type(screen.getByLabelText("Search"), "nusantara");
    expect(roles()).toEqual(["Data Engineer"]);
  });

  test("filters by status and clears filters from the empty state", async () => {
    const { user, roles } = setup();
    await user.selectOptions(screen.getByLabelText("Status"), "offer");
    expect(roles()).toEqual(["Frontend Developer"]);
    await user.type(screen.getByLabelText("Search"), "kopi");
    expect(screen.getByText("No applications match your filters")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Clear filters" }));
    expect(roles()).toHaveLength(3);
    expect(screen.getByLabelText("Status")).toHaveValue("all");
  });

  test("deletes by id with a pending state", async () => {
    let finish!: () => void;
    const onDelete = vi.fn(() => new Promise<void>((resolve) => (finish = resolve)));
    const { user } = setup(onDelete);
    await user.click(screen.getByRole("button", { name: "Delete Frontend Developer" }));
    expect(onDelete).toHaveBeenCalledWith(13);
    const button = screen.getByRole("button", { name: "Delete Frontend Developer" });
    expect(button).toBeDisabled();
    expect(button).toHaveTextContent("Deleting…");
    finish();
    await vi.waitFor(() => expect(button).toBeEnabled());
  });

  test("shows an error when deleting fails", async () => {
    const { user } = setup(vi.fn().mockRejectedValue(new Error("500")));
    await user.click(screen.getByRole("button", { name: "Delete Backend Engineer" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Couldn't delete Backend Engineer");
  });
});

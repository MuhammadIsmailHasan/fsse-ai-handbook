import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import { ApplicationForm, SearchBox } from "./application-form";

const COMPANIES = [
  { id: 3, name: "Kopi Data" },
  { id: 5, name: "Lintas AI" },
];

test("valid submit sends a typed payload and resets", async () => {
  const user = userEvent.setup();
  const onSubmit = vi.fn();
  render(<ApplicationForm onSubmit={onSubmit} companies={COMPANIES} />);
  await user.selectOptions(screen.getByLabelText("Company"), "Lintas AI");
  await user.type(screen.getByLabelText("Role"), "  AI Engineer ");
  await user.type(screen.getByLabelText("Maximum salary"), "25000000");
  await user.click(screen.getByLabelText("Remote"));
  await user.type(screen.getByLabelText("Notes"), "Referral from Budi");
  expect(screen.getByText("18/500")).toBeInTheDocument();
  await user.click(screen.getByRole("button", { name: "Save application" }));
  expect(onSubmit).toHaveBeenCalledWith({ companyId: 5, role: "AI Engineer", salaryMin: null, salaryMax: 25_000_000, remote: true, notes: "Referral from Budi" });
  expect(screen.getByLabelText("Role")).toHaveValue("");
  expect(screen.getByLabelText("Company")).toHaveValue("");
  expect(screen.getByLabelText("Remote")).not.toBeChecked();
  expect(screen.getByText("0/500")).toBeInTheDocument();
});

test("invalid submit shows linked errors and focuses the first", async () => {
  const user = userEvent.setup();
  const onSubmit = vi.fn();
  render(<ApplicationForm onSubmit={onSubmit} companies={COMPANIES} />);
  await user.type(screen.getByLabelText("Role"), "   ");
  await user.type(screen.getByLabelText("Minimum salary"), "20000000");
  await user.type(screen.getByLabelText("Maximum salary"), "9000000");
  await user.click(screen.getByRole("button", { name: "Save application" }));
  expect(onSubmit).not.toHaveBeenCalled();
  expect(screen.getByLabelText("Company")).toHaveAccessibleDescription("Choose a company");
  expect(screen.getByLabelText("Company")).toHaveAttribute("aria-invalid", "true");
  expect(screen.getByLabelText("Role")).toHaveAccessibleDescription("Role is required");
  expect(screen.getByLabelText("Maximum salary")).toHaveAccessibleDescription("Maximum must be at least the minimum");
  expect(screen.getByLabelText("Company")).toHaveFocus();
  expect(screen.getByLabelText("Role")).toHaveValue("   ");

  await user.selectOptions(screen.getByLabelText("Company"), "Kopi Data");
  await user.click(screen.getByRole("button", { name: "Save application" }));
  expect(screen.getByLabelText("Company")).not.toHaveAttribute("aria-invalid");
  expect(screen.queryByText("Choose a company", { selector: "p" })).toBeNull();
  expect(screen.getByLabelText("Role")).toHaveFocus();
});

test("inputs are controlled (value comes from state)", async () => {
  const user = userEvent.setup();
  render(<ApplicationForm onSubmit={() => {}} companies={COMPANIES} />);
  const role = screen.getByLabelText("Role") as HTMLInputElement;
  await user.type(role, "Dev");
  expect(role.value).toBe("Dev");
  expect(screen.getByLabelText("Maximum salary")).toHaveAttribute("type", "number");
  expect(screen.getByLabelText("Notes")).toHaveAttribute("maxlength", "500");
});

test("SearchBox is controlled, clears and refocuses", async () => {
  const user = userEvent.setup();
  const spy = vi.fn();
  function Parent() {
    const [q, setQ] = useState("");
    return (
      <SearchBox
        value={q}
        onChange={(v) => {
          spy(v);
          setQ(v);
        }}
      />
    );
  }
  render(<Parent />);
  const input = screen.getByRole("searchbox", { name: "Search applications" });
  expect(screen.queryByRole("button", { name: "Clear" })).toBeNull();
  await user.type(input, "kopi");
  expect(input).toHaveValue("kopi");
  await user.click(screen.getByRole("button", { name: "Clear" }));
  expect(spy).toHaveBeenLastCalledWith("");
  expect(input).toHaveValue("");
  expect(input).toHaveFocus();
  expect(screen.queryByRole("button", { name: "Clear" })).toBeNull();
});

test("types compile", () => {
  expect(typecheckFolder(import.meta.dirname).output).toBe("");
});

import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { readFileSync } from "node:fs";
import { expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import { Avatar, Button, Card, StatusBadge } from "./ui-kit";

test("Button defaults, forwarding and variants", async () => {
  const onClick = vi.fn();
  render(
    <Button onClick={onClick} aria-describedby="hint" className="extra">
      Save
    </Button>,
  );
  const button = screen.getByRole("button", { name: "Save" });
  expect(button).toHaveAttribute("type", "button");
  expect(button).toHaveAttribute("data-variant", "primary");
  expect(button).toHaveAttribute("aria-describedby", "hint");
  expect(button).toHaveClass("extra");
  await userEvent.setup().click(button);
  expect(onClick).toHaveBeenCalledTimes(1);
});

test("Button submit type, danger variant and loading", async () => {
  const onClick = vi.fn();
  const { rerender } = render(<Button type="submit" variant="danger">Delete</Button>);
  expect(screen.getByRole("button", { name: "Delete" })).toHaveAttribute("type", "submit");
  expect(screen.getByRole("button")).toHaveAttribute("data-variant", "danger");
  rerender(
    <Button loading onClick={onClick}>
      Delete
    </Button>,
  );
  const loading = screen.getByRole("button", { name: "Loading…" });
  expect(loading).toBeDisabled();
  expect(loading).toHaveAttribute("aria-busy", "true");
  await userEvent.setup().click(loading);
  expect(onClick).not.toHaveBeenCalled();
  rerender(<Button>Delete</Button>);
  expect(screen.getByRole("button")).not.toHaveAttribute("aria-busy");
});

test("Avatar image or initials", () => {
  const { rerender } = render(<Avatar name="Siti Rahma" src="/siti.png" size={32} />);
  const img = screen.getByRole("img", { name: "Siti Rahma" });
  expect(img.tagName).toBe("IMG");
  expect(img).toHaveAttribute("width", "32");
  rerender(<Avatar name="siti rahma wijaya" />);
  expect(screen.getByRole("img", { name: "siti rahma wijaya" })).toHaveTextContent(/^SR$/);
  rerender(<Avatar name="  Budi " />);
  expect(screen.getByRole("img", { name: "Budi" })).toHaveTextContent(/^B$/);
});

test("StatusBadge", () => {
  render(<StatusBadge status="interview" />);
  expect(screen.getByText("Interview")).toHaveAttribute("data-status", "interview");
});

test("Card is a labelled region with optional actions", () => {
  const { rerender } = render(
    <Card title="Notes" actions={<Button>Add note</Button>}>
      <p>Recruiter called</p>
    </Card>,
  );
  const region = screen.getByRole("region", { name: "Notes" });
  expect(within(region).getByRole("button", { name: "Add note" })).toBeInTheDocument();
  expect(within(region).getByText("Recruiter called")).toBeInTheDocument();
  rerender(
    <>
      <Card title="A">
        <p>1</p>
      </Card>
      <Card title="B">
        <p>2</p>
      </Card>
    </>,
  );
  const [a, b] = screen.getAllByRole("region");
  expect(a!.getAttribute("aria-labelledby")).not.toBe(b!.getAttribute("aria-labelledby"));
  expect(within(a!).queryByRole("button")).toBeNull();
});

test("typed props (no any)", () => {
  expect(readFileSync(`${import.meta.dirname}/ui-kit.tsx`, "utf8")).not.toMatch(/\bany\b/);
  expect(typecheckFolder(import.meta.dirname).output).toBe("");
});

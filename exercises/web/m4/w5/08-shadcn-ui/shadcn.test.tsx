import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import { DeleteApplicationDialog } from "./components/delete-application-dialog";
import { Badge, badgeVariants, StatusBadge } from "./components/ui/badge";

describe("badge", () => {
  test("variants", () => {
    const base = "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium";
    expect(badgeVariants()).toBe(`${base} bg-slate-100 text-slate-700`);
    expect(badgeVariants({ tone: "danger" })).toBe(`${base} bg-red-100 text-red-800`);
    expect(badgeVariants({ tone: "info" })).toContain("bg-blue-100 text-blue-800");
  });

  test("Badge merges classes with cn", () => {
    render(
      <Badge tone="success" className="bg-purple-100 ml-2" title="x">
        Hired
      </Badge>,
    );
    const badge = screen.getByText("Hired");
    expect(badge.tagName).toBe("SPAN");
    expect(badge).toHaveAttribute("data-slot", "badge");
    expect(badge).toHaveAttribute("title", "x");
    expect(badge.className.split(" ")).toEqual(expect.arrayContaining(["bg-purple-100", "text-green-800", "ml-2"]));
    expect(badge.className).not.toContain("bg-green-100");
  });

  test("StatusBadge", () => {
    render(
      <>
        <StatusBadge status="applied" />
        <StatusBadge status="interview" />
        <StatusBadge status="offer" />
        <StatusBadge status="rejected" />
      </>,
    );
    expect(screen.getByText("Applied")).toHaveClass("bg-blue-100");
    expect(screen.getByText("Interview")).toHaveClass("bg-amber-100");
    expect(screen.getByText("Offer 🎉")).toHaveClass("bg-green-100");
    expect(screen.getByText("Rejected")).toHaveClass("bg-red-100");
  });
});

describe("DeleteApplicationDialog", () => {
  test("opens an accessible alert dialog and cancel closes it", async () => {
    const onConfirm = vi.fn();
    const user = userEvent.setup();
    render(<DeleteApplicationDialog role="Data Engineer" onConfirm={onConfirm} />);
    const trigger = screen.getByRole("button", { name: "Delete" });
    expect(trigger).toHaveClass("bg-red-600");
    expect(screen.queryByRole("alertdialog")).not.toBeInTheDocument();
    await user.click(trigger);
    const dialog = await screen.findByRole("alertdialog");
    expect(dialog).toHaveAccessibleName('Delete "Data Engineer"?');
    expect(dialog).toHaveAccessibleDescription("This removes the application and its notes. This can't be undone.");
    await user.click(screen.getByRole("button", { name: "Cancel" }));
    await waitFor(() => expect(screen.queryByRole("alertdialog")).not.toBeInTheDocument());
    expect(onConfirm).not.toHaveBeenCalled();
  });

  test("stays open while deleting, then closes", async () => {
    let finish!: () => void;
    const onConfirm = vi.fn(() => new Promise<void>((resolve) => (finish = resolve)));
    const user = userEvent.setup();
    render(<DeleteApplicationDialog role="Data Engineer" onConfirm={onConfirm} />);
    await user.click(screen.getByRole("button", { name: "Delete" }));
    await user.click(await screen.findByRole("button", { name: "Delete application" }));
    expect(screen.getByRole("alertdialog")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Deleting…" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Cancel" })).toBeDisabled();
    await user.keyboard("{Escape}");
    expect(screen.getByRole("alertdialog")).toBeInTheDocument();
    finish();
    await waitFor(() => expect(screen.queryByRole("alertdialog")).not.toBeInTheDocument());
    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  test("shows an error and allows retry", async () => {
    const onConfirm = vi.fn().mockRejectedValueOnce(new Error("500")).mockResolvedValueOnce(undefined);
    const user = userEvent.setup();
    render(<DeleteApplicationDialog role="Data Engineer" onConfirm={onConfirm} />);
    await user.click(screen.getByRole("button", { name: "Delete" }));
    await user.click(await screen.findByRole("button", { name: "Delete application" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Couldn't delete. Try again.");
    expect(screen.getByRole("alertdialog")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Delete application" }));
    await waitFor(() => expect(screen.queryByRole("alertdialog")).not.toBeInTheDocument());
  });
});

test("types", () => {
  expect(typecheckFolder(import.meta.dirname, { recursive: true }).output).toBe("");
});

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { readFileSync } from "node:fs";
import { useState } from "react";
import { expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import { ApplicationCounter, SaveButton, SavedJobsBoard } from "./saved-jobs";

const source = readFileSync(`${import.meta.dirname}/saved-jobs.tsx`, "utf8");

test("marked as a client component", () => {
  expect(source.trimStart()).toMatch(/^["']use client["'];?/);
});

test("SaveButton is controlled by its parent", async () => {
  const onToggle = vi.fn();
  const { rerender } = render(<SaveButton saved={false} onToggle={onToggle} jobTitle="AI Engineer" />);
  const button = screen.getByRole("button", { name: "Save AI Engineer" });
  expect(button).toHaveAttribute("aria-pressed", "false");
  expect(button).toHaveAttribute("type", "button");
  expect(button).toHaveTextContent("Save");
  await userEvent.setup().click(button);
  expect(onToggle).toHaveBeenCalledTimes(1);
  expect(button).toHaveAttribute("aria-pressed", "false");
  rerender(<SaveButton saved onToggle={onToggle} jobTitle="AI Engineer" />);
  expect(screen.getByRole("button", { name: "Unsave AI Engineer" })).toHaveTextContent("Saved");
});

test("SaveButton works with any parent state", async () => {
  function Parent() {
    const [saved, setSaved] = useState(false);
    return <SaveButton saved={saved} onToggle={() => setSaved((s) => !s)} jobTitle="QA" />;
  }
  render(<Parent />);
  await userEvent.setup().click(screen.getByRole("button", { name: "Save QA" }));
  expect(screen.getByRole("button", { name: "Unsave QA" })).toHaveAttribute("aria-pressed", "true");
});

test("SavedJobsBoard lifts state up", async () => {
  const user = userEvent.setup();
  render(
    <SavedJobsBoard
      jobs={[
        { id: 1, title: "Backend Engineer" },
        { id: 2, title: "AI Engineer" },
      ]}
    />,
  );
  expect(screen.getByRole("heading", { level: 2, name: "Jobs" })).toBeInTheDocument();
  const status = () => document.querySelector('[aria-live="polite"]')?.textContent;
  const clear = screen.getByRole("button", { name: "Clear saved" });
  expect(status()).toBe("0 saved");
  expect(clear).toBeDisabled();
  await user.click(screen.getByRole("button", { name: "Save Backend Engineer" }));
  await user.click(screen.getByRole("button", { name: "Save AI Engineer" }));
  expect(status()).toBe("2 saved");
  await user.click(screen.getByRole("button", { name: "Unsave AI Engineer" }));
  expect(status()).toBe("1 saved");
  expect(clear).toBeEnabled();
  await user.click(clear);
  expect(status()).toBe("0 saved");
  expect(screen.queryAllByRole("button", { pressed: true })).toHaveLength(0);
});

test("updater functions batch correctly", async () => {
  const user = userEvent.setup();
  render(<ApplicationCounter />);
  await user.click(screen.getByRole("button", { name: "+1" }));
  await user.click(screen.getByRole("button", { name: "+3" }));
  expect(screen.getByText("Applications sent: 4")).toBeInTheDocument();
});

test("no state mutation and types compile", () => {
  expect(source).not.toMatch(/savedIds\.(add|delete|clear)\(/);
  expect(typecheckFolder(import.meta.dirname).output).toBe("");
});

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import { Tabs } from "./tabs";

function Example({ onValueChange }: { onValueChange?: (v: string) => void }) {
  return (
    <Tabs defaultValue="notes" onValueChange={onValueChange}>
      <Tabs.List aria-label="Application sections">
        <Tabs.Trigger value="notes">Notes</Tabs.Trigger>
        <Tabs.Trigger value="history">History</Tabs.Trigger>
        <Tabs.Trigger value="files" disabled>
          Files
        </Tabs.Trigger>
        <Tabs.Trigger value="ai">AI match</Tabs.Trigger>
      </Tabs.List>
      <Tabs.Panel value="notes">Notes content</Tabs.Panel>
      <Tabs.Panel value="history">History content</Tabs.Panel>
      <Tabs.Panel value="files">Files content</Tabs.Panel>
      <Tabs.Panel value="ai">AI content</Tabs.Panel>
    </Tabs>
  );
}

describe("Tabs", () => {
  test("ARIA wiring", () => {
    render(<Example />);
    expect(screen.getByRole("tablist", { name: "Application sections" })).toBeInTheDocument();
    const notes = screen.getByRole("tab", { name: "Notes" });
    const history = screen.getByRole("tab", { name: "History" });
    expect(notes).toHaveAttribute("aria-selected", "true");
    expect(history).toHaveAttribute("aria-selected", "false");
    expect(notes).toHaveAttribute("tabindex", "0");
    expect(history).toHaveAttribute("tabindex", "-1");
    expect(notes).toHaveAttribute("type", "button");
    const panel = screen.getByRole("tabpanel");
    expect(panel).toHaveTextContent("Notes content");
    expect(panel).toHaveAccessibleName("Notes");
    expect(notes.getAttribute("aria-controls")).toBe(panel.id);
    expect(panel).toHaveAttribute("tabindex", "0");
    expect(screen.queryByText("History content")).not.toBeInTheDocument();
  });

  test("click selects and notifies", async () => {
    const onValueChange = vi.fn();
    const user = userEvent.setup();
    render(<Example onValueChange={onValueChange} />);
    await user.click(screen.getByRole("tab", { name: "History" }));
    expect(screen.getByRole("tabpanel")).toHaveTextContent("History content");
    expect(onValueChange).toHaveBeenCalledWith("history");
    await user.click(screen.getByRole("tab", { name: "History" }));
    expect(onValueChange).toHaveBeenCalledTimes(1);
    await user.click(screen.getByRole("tab", { name: "Files" }));
    expect(screen.getByRole("tabpanel")).toHaveTextContent("History content");
  });

  test("keyboard: arrows skip disabled tabs and wrap, Home/End", async () => {
    const user = userEvent.setup();
    render(<Example />);
    await user.tab();
    expect(screen.getByRole("tab", { name: "Notes" })).toHaveFocus();
    await user.keyboard("{ArrowRight}");
    expect(screen.getByRole("tab", { name: "History" })).toHaveFocus();
    expect(screen.getByRole("tabpanel")).toHaveTextContent("History content");
    await user.keyboard("{ArrowRight}");
    expect(screen.getByRole("tab", { name: "AI match" })).toHaveFocus();
    await user.keyboard("{ArrowRight}");
    expect(screen.getByRole("tab", { name: "Notes" })).toHaveFocus();
    await user.keyboard("{ArrowLeft}");
    expect(screen.getByRole("tab", { name: "AI match" })).toHaveAttribute("aria-selected", "true");
    await user.keyboard("{Home}");
    expect(screen.getByRole("tab", { name: "Notes" })).toHaveFocus();
    await user.keyboard("{End}");
    expect(screen.getByRole("tabpanel")).toHaveTextContent("AI content");
    await user.tab();
    expect(screen.getByRole("tabpanel")).toHaveFocus();
  });

  test("controlled mode", async () => {
    function Controlled() {
      const [tab, setTab] = useState("history");
      return (
        <>
          <output>{tab}</output>
          <Tabs value={tab} onValueChange={(v) => v !== "ai" && setTab(v)}>
            <Tabs.List>
              <Tabs.Trigger value="notes">Notes</Tabs.Trigger>
              <Tabs.Trigger value="history">History</Tabs.Trigger>
              <Tabs.Trigger value="ai">AI match</Tabs.Trigger>
            </Tabs.List>
            <Tabs.Panel value="notes">Notes content</Tabs.Panel>
            <Tabs.Panel value="history">History content</Tabs.Panel>
            <Tabs.Panel value="ai">AI content</Tabs.Panel>
          </Tabs>
        </>
      );
    }
    const user = userEvent.setup();
    render(<Controlled />);
    expect(screen.getByRole("tabpanel")).toHaveTextContent("History content");
    await user.click(screen.getByRole("tab", { name: "AI match" }));
    expect(screen.getByRole("tabpanel")).toHaveTextContent("History content");
    await user.click(screen.getByRole("tab", { name: "Notes" }));
    expect(screen.getByRole("status")).toHaveTextContent("notes");
    expect(screen.getByRole("tabpanel")).toHaveTextContent("Notes content");
  });

  test("unique ids per instance and helpful errors", () => {
    render(
      <>
        <Example />
        <Example />
      </>,
    );
    const ids = screen.getAllByRole("tab").map((t) => t.id);
    expect(new Set(ids).size).toBe(ids.length);
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});
    expect(() => render(<Tabs.Trigger value="x">X</Tabs.Trigger>)).toThrow("Tabs.Trigger must be used inside <Tabs>");
    expect(() => render(<Tabs.Panel value="x">X</Tabs.Panel>)).toThrow("Tabs.Panel must be used inside <Tabs>");
    spy.mockRestore();
  });
});

test("types", () => {
  expect(typecheckFolder(import.meta.dirname).output).toBe("");
});

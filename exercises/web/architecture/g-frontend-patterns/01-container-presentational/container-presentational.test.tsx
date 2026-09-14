import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { readFileSync } from "node:fs";
import { describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import { ApplicationsContainer } from "./applications-container";
import { ApplicationsView, type Item } from "./applications-view";

const ITEMS: Item[] = [
  { id: 1, role: "Backend Engineer", company: "Kopi Data", status: "applied" },
  { id: 2, role: "Data Engineer", company: "Batik Cloud", status: "offer" },
];
const noop = () => {};

describe("ApplicationsView (no mocks needed)", () => {
  test("loading, empty and ready states", () => {
    const { rerender } = render(<ApplicationsView state={{ kind: "loading" }} status="all" onStatusChange={noop} onRetry={noop} />);
    expect(screen.getByRole("status")).toHaveTextContent("Loading applications…");
    rerender(<ApplicationsView state={{ kind: "ready", items: [] }} status="all" onStatusChange={noop} onRetry={noop} />);
    expect(screen.getByText("No applications")).toBeInTheDocument();
    rerender(<ApplicationsView state={{ kind: "ready", items: ITEMS }} status="offer" onStatusChange={noop} onRetry={noop} />);
    expect(screen.getAllByRole("listitem").map((li) => li.textContent)).toEqual(["Backend Engineer — Kopi Data (applied)", "Data Engineer — Batik Cloud (offer)"]);
    expect(screen.getByLabelText("Status")).toHaveValue("offer");
    expect(screen.getAllByRole("option").map((o) => o.textContent)).toEqual(["All", "Applied", "Interview", "Offer", "Rejected"]);
  });

  test("error state and callbacks", async () => {
    const onRetry = vi.fn();
    const onStatusChange = vi.fn();
    const user = userEvent.setup();
    render(<ApplicationsView state={{ kind: "error", message: "Boom" }} status="all" onStatusChange={onStatusChange} onRetry={onRetry} />);
    expect(screen.getByRole("alert")).toHaveTextContent("Boom");
    await user.click(screen.getByRole("button", { name: "Retry" }));
    expect(onRetry).toHaveBeenCalledTimes(1);
    await user.selectOptions(screen.getByLabelText("Status"), "interview");
    expect(onStatusChange).toHaveBeenCalledWith("interview");
  });

  test("is purely presentational", () => {
    const source = readFileSync(`${import.meta.dirname}/applications-view.tsx`, "utf8");
    expect(source).not.toMatch(/\bfetch\(|use(State|Effect|Reducer|Context|Ref)\b/);
    expect(source).not.toMatch(/import\s+(?!type)[^;]*from\s+["']react["']/);
  });
});

describe("ApplicationsContainer (injected loader)", () => {
  test("loads, filters and passes the status to the loader", async () => {
    const load = vi.fn(async (status: string) => ITEMS.filter((i) => status === "all" || i.status === status));
    const user = userEvent.setup();
    render(<ApplicationsContainer loadApplications={load} />);
    expect(screen.getByRole("status")).toHaveTextContent("Loading applications…");
    expect(await screen.findAllByRole("listitem")).toHaveLength(2);
    await user.selectOptions(screen.getByLabelText("Status"), "offer");
    expect(await screen.findByText("Data Engineer — Batik Cloud (offer)")).toBeInTheDocument();
    expect(screen.getAllByRole("listitem")).toHaveLength(1);
    expect(load.mock.calls.map((c) => c[0])).toEqual(["all", "offer"]);
  });

  test("errors and retry", async () => {
    const load = vi.fn().mockRejectedValueOnce(new Error("500")).mockResolvedValueOnce(ITEMS);
    const user = userEvent.setup();
    render(<ApplicationsContainer loadApplications={load} />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Couldn't load applications");
    await user.click(screen.getByRole("button", { name: "Retry" }));
    expect(await screen.findAllByRole("listitem")).toHaveLength(2);
    expect(load).toHaveBeenCalledTimes(2);
  });

  test("aborts and ignores stale responses", async () => {
    const pending: { status: string; signal: AbortSignal; resolve: (items: Item[]) => void }[] = [];
    const load = vi.fn((status: string, signal: AbortSignal) => new Promise<Item[]>((resolve) => pending.push({ status, signal, resolve })));
    const user = userEvent.setup();
    render(<ApplicationsContainer loadApplications={load} />);
    await user.selectOptions(screen.getByLabelText("Status"), "offer");
    expect(pending[0]!.signal.aborted).toBe(true);
    await act(async () => pending[1]!.resolve([ITEMS[1]!]));
    await act(async () => pending[0]!.resolve(ITEMS));
    expect(screen.getAllByRole("listitem")).toHaveLength(1);
  });
});

test("types", () => {
  expect(typecheckFolder(import.meta.dirname).output).toBe("");
});

import { render, renderHook, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { memo, Profiler } from "react";
import { afterEach, describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import { CompareButton, CompareStoreProvider, CompareTray, createCompareStore, selectCount, selectIsSelected, useCompareStore } from "./compare-store";

afterEach(() => localStorage.clear());

describe("store", () => {
  test("toggle rules and max 3", () => {
    const store = createCompareStore();
    const s = () => store.getState();
    expect(s().jobIds).toEqual([]);
    expect(s().isTrayOpen).toBe(false);
    expect(s().toggleJob(1)).toBe("added");
    expect(s().isTrayOpen).toBe(true);
    const before = s().jobIds;
    s().toggleJob(2);
    expect(before).toEqual([1]);
    s().toggleJob(3);
    expect(s().toggleJob(4)).toBe("full");
    expect(s().jobIds).toEqual([1, 2, 3]);
    expect(s().toggleJob(2)).toBe("removed");
    expect(s().jobIds).toEqual([1, 3]);
    expect(selectCount(s())).toBe(2);
    expect(selectIsSelected(3)(s())).toBe(true);
    expect(selectIsSelected(2)(s())).toBe(false);
    s().setTrayOpen(false);
    expect(s().isTrayOpen).toBe(false);
    s().clear();
    expect(s()).toMatchObject({ jobIds: [], isTrayOpen: false });
  });

  test("separate stores don't share state", () => {
    const a = createCompareStore();
    const b = createCompareStore({ jobIds: [9] });
    a.getState().toggleJob(1);
    expect(b.getState().jobIds).toEqual([9]);
  });

  test("persists only jobIds under careerpilot-compare", () => {
    const store = createCompareStore();
    store.getState().toggleJob(5);
    const saved = JSON.parse(localStorage.getItem("careerpilot-compare")!);
    expect(saved.state).toEqual({ jobIds: [5] });
    const restored = createCompareStore();
    expect(restored.getState().jobIds).toEqual([5]);
    expect(restored.getState().isTrayOpen).toBe(false);
  });
});

describe("react bindings", () => {
  test("hook requires the provider", () => {
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});
    expect(() => renderHook(() => useCompareStore(selectCount))).toThrow("useCompareStore must be used inside <CompareStoreProvider>");
    spy.mockRestore();
  });

  test("buttons, tray and fine-grained re-renders", async () => {
    const renders = new Map<number, number>();
    const TrackedButton = memo(function TrackedButton({ jobId }: { jobId: number }) {
      renders.set(jobId, (renders.get(jobId) ?? 0) + 1);
      return (
        <li data-testid={`job-${jobId}`}>
          <CompareButton jobId={jobId} />
        </li>
      );
    });
    const user = userEvent.setup();
    render(
      <CompareStoreProvider>
        <ul>
          {[1, 2, 3, 4].map((id) => (
            <TrackedButton key={id} jobId={id} />
          ))}
        </ul>
        <CompareTray />
      </CompareStoreProvider>,
    );
    const button = (id: number) => within(screen.getByTestId(`job-${id}`)).getByRole("button", { name: "Compare" });
    expect(screen.queryByRole("complementary")).not.toBeInTheDocument();

    await user.click(button(1));
    expect(button(1)).toHaveAttribute("aria-pressed", "true");
    expect(button(2)).toHaveAttribute("aria-pressed", "false");
    const tray = screen.getByRole("complementary", { name: "Compare jobs" });
    expect(within(tray).getByRole("heading")).toHaveTextContent("Compare (1/3)");

    await user.click(button(2));
    await user.click(button(3));
    await user.click(button(4));
    expect(within(screen.getByTestId("job-4")).getByRole("status")).toHaveTextContent("You can compare up to 3 jobs");
    expect(button(4)).toHaveAttribute("aria-pressed", "false");
    expect(screen.getByRole("heading")).toHaveTextContent("Compare (3/3)");

    await user.click(screen.getByRole("button", { name: "Clear" }));
    expect(screen.queryByRole("complementary")).not.toBeInTheDocument();
    expect(button(1)).toHaveAttribute("aria-pressed", "false");
    expect([...renders.values()]).toEqual([1, 1, 1, 1]);
  });

  test("CompareButton subscribes narrowly (measured with React Profiler)", async () => {
    const commits = { job1: 0, job2: 0 };
    const user = userEvent.setup();
    render(
      <CompareStoreProvider>
        <Profiler id="job1" onRender={() => commits.job1++}>
          <CompareButton jobId={1} />
        </Profiler>
        <Profiler id="job2" onRender={() => commits.job2++}>
          <CompareButton jobId={2} />
        </Profiler>
      </CompareStoreProvider>,
    );
    const [first, second] = screen.getAllByRole("button", { name: "Compare" });
    await user.click(second!);
    await user.click(second!);
    expect(commits.job2).toBe(3);
    expect(commits.job1).toBe(1);
    expect(first).toHaveAttribute("aria-pressed", "false");
  });
});

test("types", () => {
  expect(typecheckFolder(import.meta.dirname).output).toBe("");
});

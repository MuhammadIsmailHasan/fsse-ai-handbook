import { describe, expect, test, vi } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import { createStore, firstOrNull, groupBy, paginate, pick, tryCatch } from "./generic-utils";

const JOBS = [
  { id: 1, title: "Backend", status: "applied" },
  { id: 2, title: "AI", status: "saved" },
  { id: 3, title: "QA", status: "applied" },
];

test("groupBy", () => {
  expect(groupBy(JOBS, (j) => j.status)).toEqual({ applied: [JOBS[0], JOBS[2]], saved: [JOBS[1]] });
  expect(groupBy([], (x: number) => x)).toEqual({});
});

test("pick", () => {
  const original = { id: 1, title: "Backend", secret: "x" };
  const picked = pick(original, ["id", "title"]);
  expect(picked).toEqual({ id: 1, title: "Backend" });
  expect(original).toHaveProperty("secret");
});

describe("tryCatch", () => {
  test("wraps success and failures without throwing", async () => {
    await expect(tryCatch(async () => 42)).resolves.toEqual({ ok: true, value: 42 });
    const failure = await tryCatch(async () => {
      throw new TypeError("boom");
    });
    expect(failure.ok).toBe(false);
    expect(!failure.ok && failure.error).toBeInstanceOf(TypeError);
    const weird = await tryCatch(async () => {
      throw "just a string";
    });
    expect(!weird.ok && weird.error.message).toBe("just a string");
  });
});

test("paginate", () => {
  const items = Array.from({ length: 45 }, (_, i) => i + 1);
  expect(paginate(items, 1, 20)).toEqual({ data: items.slice(0, 20), meta: { page: 1, perPage: 20, total: 45, totalPages: 3 } });
  expect(paginate(items, 3, 20).data).toEqual([41, 42, 43, 44, 45]);
  expect(paginate(items, 4, 20).data).toEqual([]);
  expect(paginate(items, 0, 20).data).toEqual([]);
  expect(paginate([], 1, 10).meta).toEqual({ page: 1, perPage: 10, total: 0, totalPages: 1 });
});

test("createStore", () => {
  const store = createStore({ saved: 0 });
  const listener = vi.fn();
  const unsubscribe = store.subscribe(listener);
  store.set((prev) => ({ saved: prev.saved + 1 }));
  expect(store.get()).toEqual({ saved: 1 });
  expect(listener).toHaveBeenCalledWith({ saved: 1 });
  const same = store.get();
  store.set(same);
  expect(listener).toHaveBeenCalledTimes(1);
  unsubscribe();
  store.set({ saved: 5 });
  expect(listener).toHaveBeenCalledTimes(1);
  expect(store.get()).toEqual({ saved: 5 });
});

test("firstOrNull", () => {
  expect(firstOrNull([7, 8])).toBe(7);
  expect(firstOrNull([])).toBeNull();
});

test("types flow through (tsc strict)", () => {
  expect(typecheckFolder(import.meta.dirname).output).toBe("");
});

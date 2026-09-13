import { readFileSync } from "node:fs";
import { expect, test } from "vitest";
import { typecheckFolder } from "@support/typecheck";
import { STATUS_LABELS, countByStatus, isStatus, moveItem, sortBy, withTag, type BoardItem } from "./board";

const ITEMS: readonly BoardItem[] = Object.freeze([
  Object.freeze({ id: 3, title: "QA", status: "offer", tags: ["remote"] }),
  Object.freeze({ id: 1, title: "Backend", status: "applied", tags: [] }),
  Object.freeze({ id: 2, title: "AI", status: "applied", tags: ["python"] }),
]) as readonly BoardItem[];

test("labels and guard", () => {
  expect(STATUS_LABELS).toEqual({ saved: "Saved", applied: "Applied", interview: "Interview", offer: "Offer", rejected: "Rejected" });
  expect(isStatus("offer")).toBe(true);
  expect(isStatus("ghosted")).toBe(false);
  expect(isStatus(3)).toBe(false);
});

test("countByStatus includes zeros", () => {
  expect(countByStatus(ITEMS)).toEqual({ saved: 0, applied: 2, interview: 0, offer: 1, rejected: 0 });
});

test("moveItem is immutable and keeps untouched items", () => {
  const moved = moveItem(ITEMS, 1, "interview");
  expect(moved).not.toBe(ITEMS);
  expect(moved.map((i) => i.status)).toEqual(["offer", "interview", "applied"]);
  expect(moved[0]).toBe(ITEMS[0]);
  expect(ITEMS[1]!.status).toBe("applied");
  expect(moveItem(ITEMS, 99, "saved")).toEqual(ITEMS);
});

test("withTag never duplicates or mutates", () => {
  const tagged = withTag(ITEMS[1]!, "urgent");
  expect(tagged.tags).toEqual(["urgent"]);
  expect(ITEMS[1]!.tags).toEqual([]);
  const again = withTag(ITEMS[0]!, "remote");
  expect(again.tags).toEqual(["remote"]);
  expect(again).not.toBe(ITEMS[0]);
});

test("sortBy", () => {
  expect(sortBy(ITEMS, "id").map((i) => i.id)).toEqual([1, 2, 3]);
  expect(sortBy(ITEMS, "title").map((i) => i.title)).toEqual(["AI", "Backend", "QA"]);
  expect(sortBy(ITEMS, "status").map((i) => i.id)).toEqual([1, 2, 3]);
});

test("types (tsc strict) and satisfies", () => {
  const source = readFileSync(`${import.meta.dirname}/board.ts`, "utf8");
  expect(source).toMatch(/as const/);
  expect(source).toMatch(/satisfies Record<Status, string>/);
  expect(typecheckFolder(import.meta.dirname).output).toBe("");
});

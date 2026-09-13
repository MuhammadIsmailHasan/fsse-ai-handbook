// Type-level checks. Don't edit.
import { expectTypeOf } from "vitest";
import { STATUSES, STATUS_LABELS, countByStatus, isStatus, sortBy, type BoardItem, type Status } from "./board";

expectTypeOf<Status>().toEqualTypeOf<"saved" | "applied" | "interview" | "offer" | "rejected">();
expectTypeOf(STATUSES).toEqualTypeOf<readonly ["saved", "applied", "interview", "offer", "rejected"]>();
expectTypeOf(STATUS_LABELS.offer).toEqualTypeOf<string>();
expectTypeOf(countByStatus).returns.toEqualTypeOf<Record<Status, number>>();
expectTypeOf(sortBy).parameter(1).toEqualTypeOf<"id" | "title" | "status">();

const item: BoardItem = { id: 1, title: "Dev", status: "saved", tags: [] };
// @ts-expect-error — id is readonly
item.id = 2;
// @ts-expect-error — not a status
const bad: BoardItem = { id: 1, title: "Dev", status: "ghosted", tags: [] };
// @ts-expect-error — can't sort by tags
sortBy([item], "tags");
// @ts-expect-error — STATUSES is readonly
STATUSES.push("withdrawn");

declare const input: unknown;
if (isStatus(input)) expectTypeOf(input).toEqualTypeOf<Status>();

const readonlyItems: readonly BoardItem[] = [item];
countByStatus(readonlyItems); // must accept readonly arrays

export { bad };

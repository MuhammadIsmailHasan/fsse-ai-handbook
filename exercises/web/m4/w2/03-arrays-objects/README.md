# M4 · W2 · 03 — Typed Arrays, Objects and `as const`

> 🚫🤖 **No-AI** · ⏱️ ~60 min · edit **`board.ts`**

| Export | Requirement |
|---|---|
| `STATUSES` | `["saved", "applied", "interview", "offer", "rejected"] as const` |
| `type Status` | derived from `STATUSES` with an indexed access type (`(typeof STATUSES)[number]`) |
| `STATUS_LABELS` | object with a label for every status, declared with `satisfies Record<Status, string>` (so a missing or misspelled key is an error, but the literal types stay) |
| `interface BoardItem` | `readonly id: number`, `title: string`, `status: Status`, `tags: string[]` |
| `isStatus(value)` | `(value: unknown) => value is Status` |
| `countByStatus(items)` | `(items: readonly BoardItem[]) => Record<Status, number>` — every status present, zeros included |
| `moveItem(items, id, status)` | returns a **new** array where that item has the new status (other items keep their identity); unknown id → same contents in a new array |
| `withTag(item, tag)` | returns a new item with the tag added once (no duplicates), never mutating the original |
| `sortBy(items, key)` | `(items: readonly BoardItem[], key: "id" \| "title" \| "status") => BoardItem[]` — ascending, a new array; status order follows `STATUSES` |

```bash
cd exercises/web
npx vitest run m4/w2/03-arrays-objects
```

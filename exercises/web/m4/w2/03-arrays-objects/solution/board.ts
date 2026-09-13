export const STATUSES = ["saved", "applied", "interview", "offer", "rejected"] as const;
export type Status = (typeof STATUSES)[number];

export const STATUS_LABELS = {
  saved: "Saved",
  applied: "Applied",
  interview: "Interview",
  offer: "Offer",
  rejected: "Rejected",
} satisfies Record<Status, string>;

export interface BoardItem {
  readonly id: number;
  title: string;
  status: Status;
  tags: string[];
}

export function isStatus(value: unknown): value is Status {
  return typeof value === "string" && (STATUSES as readonly string[]).includes(value);
}

export function countByStatus(items: readonly BoardItem[]): Record<Status, number> {
  const counts = Object.fromEntries(STATUSES.map((status) => [status, 0])) as Record<Status, number>;
  for (const item of items) counts[item.status] += 1;
  return counts;
}

export function moveItem(items: readonly BoardItem[], id: number, status: Status): BoardItem[] {
  return items.map((item) => (item.id === id ? { ...item, status } : item));
}

export function withTag(item: BoardItem, tag: string): BoardItem {
  return item.tags.includes(tag) ? { ...item, tags: [...item.tags] } : { ...item, tags: [...item.tags, tag] };
}

export function sortBy(items: readonly BoardItem[], key: "id" | "title" | "status"): BoardItem[] {
  return items.toSorted((a, b) => {
    if (key === "id") return a.id - b.id;
    if (key === "title") return a.title.localeCompare(b.title);
    return STATUSES.indexOf(a.status) - STATUSES.indexOf(b.status);
  });
}

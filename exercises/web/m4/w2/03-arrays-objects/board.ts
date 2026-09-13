// Typed arrays and objects. See README.md.

export const STATUSES = ["saved", "applied", "interview", "offer", "rejected"];
export type Status = string;
export const STATUS_LABELS = {};

export interface BoardItem {}

export function isStatus(value: unknown): boolean {
  throw new Error("TODO");
}
export function countByStatus(items: BoardItem[]): Record<string, number> {
  throw new Error("TODO");
}
export function moveItem(items: BoardItem[], id: number, status: Status): BoardItem[] {
  throw new Error("TODO");
}
export function withTag(item: BoardItem, tag: string): BoardItem {
  throw new Error("TODO");
}
export function sortBy(items: BoardItem[], key: string): BoardItem[] {
  throw new Error("TODO");
}

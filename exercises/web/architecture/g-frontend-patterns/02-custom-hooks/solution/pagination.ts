import { useMemo } from "react";

export type PageItem = number | "…";

/** Pure: easy to test exhaustively, reusable outside React. */
export function getPageItems({ page, totalPages, siblings = 1 }: { page: number; totalPages: number; siblings?: number }): PageItem[] {
  if (totalPages <= 0) return [];
  const current = Math.min(Math.max(page, 1), totalPages);
  const wanted = new Set<number>([1, totalPages]);
  for (let p = current - siblings; p <= current + siblings; p++) if (p >= 1 && p <= totalPages) wanted.add(p);

  const sorted = [...wanted].sort((a, b) => a - b);
  const items: PageItem[] = [];
  for (const p of sorted) {
    const previous = items.at(-1);
    if (typeof previous === "number" && p - previous === 2) items.push(previous + 1); // a one-page gap: show the page
    else if (typeof previous === "number" && p - previous > 2) items.push("…");
    items.push(p);
  }
  return items;
}

export function usePagination({ total, pageSize, page, onPageChange }: { total: number; pageSize: number; page: number; onPageChange: (page: number) => void }) {
  const totalPages = Math.max(0, Math.ceil(total / pageSize));
  const current = totalPages === 0 ? 1 : Math.min(Math.max(page, 1), totalPages);
  const items = useMemo(() => getPageItems({ page: current, totalPages }), [current, totalPages]);

  const goTo = (target: number) => {
    const clamped = Math.min(Math.max(target, 1), Math.max(totalPages, 1));
    if (clamped !== current) onPageChange(clamped);
  };

  return {
    totalPages,
    items,
    hasPrevious: current > 1,
    hasNext: current < totalPages,
    previous: () => goTo(current - 1),
    next: () => goTo(current + 1),
    goTo,
  };
}

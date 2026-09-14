// See README.md.
export type PageItem = number | "…";

export function getPageItems(options: { page: number; totalPages: number; siblings?: number }): PageItem[] {
  return [];
}

export function usePagination(options: { total: number; pageSize: number; page: number; onPageChange: (page: number) => void }) {
  return { totalPages: 0, items: [] as PageItem[], hasPrevious: false, hasNext: false, previous() {}, next() {}, goTo(_page: number) {} };
}

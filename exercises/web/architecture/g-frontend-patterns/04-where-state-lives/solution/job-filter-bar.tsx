"use client";

import { useEffect, useState } from "react";
import { useJobFilters } from "./use-job-filters";

export function JobFilterBar() {
  const { filters, setFilters } = useJobFilters();
  // Local state for instant typing; the URL is updated after a pause.
  const [draft, setDraft] = useState(filters.q);
  const [syncedQ, setSyncedQ] = useState(filters.q);

  // URL changed from outside (back button, link): adopt it — adjusting state during render, no effect needed.
  if (filters.q !== syncedQ) {
    setSyncedQ(filters.q);
    setDraft(filters.q);
  }

  useEffect(() => {
    if (draft.trim() === filters.q) return;
    const timer = setTimeout(() => setFilters({ q: draft }, { history: "replace" }), 300);
    return () => clearTimeout(timer);
  });

  return (
    <form role="search" onSubmit={(event) => event.preventDefault()}>
      <label htmlFor="job-search">Search</label>
      <input id="job-search" type="search" value={draft} onChange={(event) => setDraft(event.target.value)} />

      <label htmlFor="job-status">Status</label>
      <select id="job-status" value={filters.status} onChange={(event) => setFilters({ status: event.target.value as typeof filters.status })}>
        <option value="open">Open</option>
        <option value="closed">Closed</option>
        <option value="all">All</option>
      </select>

      <label>
        <input type="checkbox" checked={filters.remote} onChange={(event) => setFilters({ remote: event.target.checked })} />
        Remote only
      </label>

      <label htmlFor="job-sort">Sort</label>
      <select id="job-sort" value={filters.sort} onChange={(event) => setFilters({ sort: event.target.value as typeof filters.sort })}>
        <option value="newest">Newest</option>
        <option value="salary">Highest salary</option>
      </select>
    </form>
  );
}

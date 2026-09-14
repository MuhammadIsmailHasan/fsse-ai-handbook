"use client";
// MUTANT: a copy with one deliberate bug (used by grade.test.ts).
import { useMemo, useState } from "react";

export type Status = "applied" | "interview" | "offer" | "rejected";
export type ApplicationRow = { id: number; role: string; company: string; status: Status; appliedOn: string };

type Props = { applications: ApplicationRow[]; onDelete: (id: number) => Promise<void> };

export function ApplicationsTable({ applications, onDelete }: Props) {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<Status | "all">("all");
  const [sortDirection, setSortDirection] = useState<"ascending" | "descending">("descending");
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [failedRole, setFailedRole] = useState<string | null>(null);

  const rows = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return applications
      .filter((a) => status === "all" || a.status === status)
      .filter((a) => !needle || a.role.toLowerCase().includes(needle) || a.company.toLowerCase().includes(needle))
      .toSorted((a, b) => (sortDirection === "ascending" ? a.appliedOn.localeCompare(b.appliedOn) : b.appliedOn.localeCompare(a.appliedOn)));
  }, [applications, query, status, sortDirection]);

  async function handleDelete(row: ApplicationRow) {
    setDeletingId(row.id);
    setFailedRole(null);
    try {
      await onDelete(row.id);
    } catch {
      setFailedRole(row.role);
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <section>
      <label htmlFor="search">Search</label>
      <input id="search" type="search" value={query} onChange={(e) => setQuery(e.target.value)} />
      <label htmlFor="status-filter">Status</label>
      <select id="status-filter" value={status} onChange={(e) => setStatus(e.target.value as Status | "all")}>
        <option value="all">All</option>
        <option value="applied">Applied</option>
        <option value="interview">Interview</option>
        <option value="offer">Offer</option>
        <option value="rejected">Rejected</option>
      </select>

      {failedRole && <p role="alert">{`Couldn't delete ${failedRole}`}</p>}

      {rows.length === 0 ? (
        <div>
          <p>No applications match your filters</p>
          <button type="button" onClick={() => { setQuery(""); setStatus("all"); }}>
            Clear filters
          </button>
        </div>
      ) : (
        <table>
          <caption>{`${rows.length} ${rows.length === 1 ? "application" : "applications"}`}</caption>
          <thead>
            <tr>
              <th scope="col">Role</th>
              <th scope="col">Company</th>
              <th scope="col">Status</th>
              <th scope="col" aria-sort="descending">
                <button type="button" onClick={() => setSortDirection((d) => (d === "ascending" ? "descending" : "ascending"))}>
                  Applied on
                </button>
              </th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id}>
                <td>{row.role}</td>
                <td>{row.company}</td>
                <td>{row.status}</td>
                <td>{row.appliedOn}</td>
                <td>
                  <button type="button" aria-label={`Delete ${row.role}`} disabled={deletingId === row.id} onClick={() => handleDelete(row)}>
                    {deletingId === row.id ? "Deleting…" : "Delete"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}

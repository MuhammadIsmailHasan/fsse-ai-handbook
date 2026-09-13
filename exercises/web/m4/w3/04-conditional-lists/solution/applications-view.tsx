"use client";

import { useState } from "react";

export type Status = "saved" | "applied" | "interview" | "offer" | "rejected";
export const STATUS_ORDER: readonly Status[] = ["saved", "applied", "interview", "offer", "rejected"];
export const STATUS_LABELS: Record<Status, string> = { saved: "Saved", applied: "Applied", interview: "Interview", offer: "Offer", rejected: "Rejected" };

export type Application = { id: number; role: string; company: string; status: Status; unread: number };

export type RequestState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "success"; data: T };

type Filter = Status | "all";

export function ApplicationsView({ state, onRetry }: { state: RequestState<Application[]>; onRetry: () => void }) {
  switch (state.status) {
    case "idle":
      return null;
    case "loading":
      return (
        <div role="status" aria-live="polite">
          Loading applications…
        </div>
      );
    case "error":
      return (
        <div role="alert">
          <p>{state.message}</p>
          <button type="button" onClick={onRetry}>
            Try again
          </button>
        </div>
      );
    case "success":
      return state.data.length === 0 ? <p>No applications yet</p> : <ApplicationGroups applications={state.data} />;
  }
}

function ApplicationGroups({ applications }: { applications: Application[] }) {
  const [filter, setFilter] = useState<Filter>("all");

  // Derived data: computed during render, not stored in state.
  const present = STATUS_ORDER.filter((status) => applications.some((app) => app.status === status));
  const visible = filter === "all" ? applications : applications.filter((app) => app.status === filter);
  const countFor = (status: Status) => applications.filter((app) => app.status === status).length;

  return (
    <>
      <div role="group" aria-label="Filter by status">
        <button type="button" aria-pressed={filter === "all"} onClick={() => setFilter("all")}>
          All ({applications.length})
        </button>
        {present.map((status) => (
          <button key={status} type="button" aria-pressed={filter === status} onClick={() => setFilter(status)}>
            {STATUS_LABELS[status]} ({countFor(status)})
          </button>
        ))}
      </div>

      {STATUS_ORDER.map((status) => {
        const items = visible.filter((app) => app.status === status);
        if (items.length === 0) return null;
        return (
          <section key={status} aria-label={STATUS_LABELS[status]}>
            <h2>{STATUS_LABELS[status]}</h2>
            <ul>
              {items.map((app) => (
                <li key={app.id}>
                  {app.role} at {app.company}
                  {app.unread > 0 && <span> {app.unread} new</span>}
                </li>
              ))}
            </ul>
          </section>
        );
      })}
    </>
  );
}

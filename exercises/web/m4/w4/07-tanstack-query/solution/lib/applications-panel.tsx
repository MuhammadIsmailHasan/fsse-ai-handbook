"use client";

import type { ApplicationsApi, Filters, Status } from "./api-types";
import { useApplications, useMoveStatus } from "./applications-hooks";

const STATUSES: Status[] = ["saved", "applied", "interview", "offer", "rejected"];

export function ApplicationsPanel({ api, filters }: { api: ApplicationsApi; filters: Filters }) {
  const query = useApplications(api, filters);
  const move = useMoveStatus(api);

  if (query.isPending) return <p role="status">Loading applications…</p>;
  if (query.isError)
    return (
      <div role="alert">
        Couldn&apos;t load applications{" "}
        <button type="button" onClick={() => void query.refetch()}>
          Retry
        </button>
      </div>
    );

  const failedRole = move.isError ? query.data.find((a) => a.id === move.variables?.id)?.role : undefined;

  return (
    <section>
      {query.isFetching && <p aria-live="polite">Updating…</p>}
      {failedRole && <p role="alert">Couldn&apos;t move {failedRole}</p>}
      <ul>
        {query.data.map((application) => (
          <li key={application.id}>
            {application.role}{" "}
            <select
              aria-label={`Status for ${application.role}`}
              value={application.status}
              onChange={(event) => move.mutate({ id: application.id, status: event.target.value as Status })}
            >
              {STATUSES.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </li>
        ))}
      </ul>
    </section>
  );
}

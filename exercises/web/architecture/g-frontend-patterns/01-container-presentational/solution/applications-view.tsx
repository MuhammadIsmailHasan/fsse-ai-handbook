// Presentational: everything comes in through props → trivial to test, reuse and put in Storybook.
export type Item = { id: number; role: string; company: string; status: string };
export type ViewState = { kind: "loading" } | { kind: "error"; message: string } | { kind: "ready"; items: Item[] };

const STATUS_OPTIONS = [
  ["all", "All"],
  ["applied", "Applied"],
  ["interview", "Interview"],
  ["offer", "Offer"],
  ["rejected", "Rejected"],
] as const;

type Props = { state: ViewState; status: string; onStatusChange: (status: string) => void; onRetry: () => void };

export function ApplicationsView({ state, status, onStatusChange, onRetry }: Props) {
  return (
    <section>
      <label htmlFor="status-filter">Status</label>
      <select id="status-filter" value={status} onChange={(event) => onStatusChange(event.target.value)}>
        {STATUS_OPTIONS.map(([value, label]) => (
          <option key={value} value={value}>
            {label}
          </option>
        ))}
      </select>

      {state.kind === "loading" && <p role="status">Loading applications…</p>}
      {state.kind === "error" && (
        <div role="alert">
          {state.message}{" "}
          <button type="button" onClick={onRetry}>
            Retry
          </button>
        </div>
      )}
      {state.kind === "ready" &&
        (state.items.length === 0 ? (
          <p>No applications</p>
        ) : (
          <ul aria-label="Applications">
            {state.items.map((item) => (
              <li key={item.id}>{`${item.role} — ${item.company} (${item.status})`}</li>
            ))}
          </ul>
        ))}
    </section>
  );
}

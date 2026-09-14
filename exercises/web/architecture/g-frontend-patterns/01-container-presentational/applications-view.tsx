// Presentational component. See README.md.
export type Item = { id: number; role: string; company: string; status: string };
export type ViewState = { kind: "loading" } | { kind: "error"; message: string } | { kind: "ready"; items: Item[] };

export function ApplicationsView(props: { state: ViewState; status: string; onStatusChange: (status: string) => void; onRetry: () => void }) {
  return null;
}

"use client";

import { useEffect, useState } from "react";
import { ApplicationsView, type Item, type ViewState } from "./applications-view";

type Props = { loadApplications: (status: string, signal: AbortSignal) => Promise<Item[]> };

// Container: owns state and side effects, delegates all markup to the view.
export function ApplicationsContainer({ loadApplications }: Props) {
  const [status, setStatus] = useState("all");
  const [state, setState] = useState<ViewState>({ kind: "loading" });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setState({ kind: "loading" });
    loadApplications(status, controller.signal).then(
      (items) => {
        if (!controller.signal.aborted) setState({ kind: "ready", items });
      },
      () => {
        if (!controller.signal.aborted) setState({ kind: "error", message: "Couldn't load applications" });
      },
    );
    return () => controller.abort();
  }, [status, attempt, loadApplications]);

  return <ApplicationsView state={state} status={status} onStatusChange={setStatus} onRetry={() => setAttempt((n) => n + 1)} />;
}

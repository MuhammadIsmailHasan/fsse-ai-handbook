"use client";
// Provided "before" code — read it, don't edit it. Your refactor goes in the other two files.
import { useEffect, useState } from "react";

export function TangledApplications() {
  const [status, setStatus] = useState("all");
  const [items, setItems] = useState<{ id: number; role: string; company: string; status: string }[] | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch(`/api/applications?status=${status}`)
      .then((r) => r.json())
      .then(setItems)
      .catch(() => setError(true));
  }, [status]);

  return (
    <div>
      <select value={status} onChange={(e) => setStatus(e.target.value)}>
        <option value="all">All</option>
        <option value="applied">Applied</option>
      </select>
      {error && <p>Error!</p>}
      {!items ? <p>Loading…</p> : items.map((i) => <div key={i.id}>{i.role}</div>)}
    </div>
  );
}

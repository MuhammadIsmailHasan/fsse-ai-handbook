"use client";

import { useState } from "react";

export type JobSummary = { id: number; title: string };

export function SaveButton({ saved, onToggle, jobTitle }: { saved: boolean; onToggle: () => void; jobTitle: string }) {
  return (
    <button type="button" aria-pressed={saved} aria-label={`${saved ? "Unsave" : "Save"} ${jobTitle}`} onClick={onToggle}>
      {saved ? "Saved" : "Save"}
    </button>
  );
}

export function SavedJobsBoard({ jobs }: { jobs: JobSummary[] }) {
  const [savedIds, setSavedIds] = useState<ReadonlySet<number>>(() => new Set());

  function toggle(id: number) {
    setSavedIds((previous) => {
      const next = new Set(previous); // new object → React sees the change
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  return (
    <section>
      <h2>Jobs</h2>
      <ul>
        {jobs.map((job) => (
          <li key={job.id}>
            {job.title} <SaveButton saved={savedIds.has(job.id)} onToggle={() => toggle(job.id)} jobTitle={job.title} />
          </li>
        ))}
      </ul>
      <p aria-live="polite">{savedIds.size} saved</p>
      <button type="button" disabled={savedIds.size === 0} onClick={() => setSavedIds(new Set())}>
        Clear saved
      </button>
    </section>
  );
}

export function ApplicationCounter() {
  const [count, setCount] = useState(0);
  return (
    <div>
      <p>Applications sent: {count}</p>
      <button type="button" onClick={() => setCount((c) => c + 1)}>
        +1
      </button>
      <button
        type="button"
        onClick={() => {
          setCount((c) => c + 1);
          setCount((c) => c + 1);
          setCount((c) => c + 1);
        }}
      >
        +3
      </button>
    </div>
  );
}

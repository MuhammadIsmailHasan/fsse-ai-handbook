"use client";

import { useState } from "react";
import { saveJob } from "../../../lib/client-api";

export function SaveJobButton({ jobId, initialSaved }: { jobId: number; initialSaved: boolean }) {
  const [saved, setSaved] = useState(initialSaved);

  async function toggle() {
    const next = !saved;
    setSaved(next); // optimistic
    try {
      await saveJob(jobId, next);
    } catch {
      setSaved(!next); // roll back
    }
  }

  return (
    <button type="button" aria-pressed={saved} onClick={toggle}>
      {saved ? "Saved" : "Save job"}
    </button>
  );
}

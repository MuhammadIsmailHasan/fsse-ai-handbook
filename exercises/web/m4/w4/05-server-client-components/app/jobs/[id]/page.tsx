"use client";
// 🚩 Everything runs in the browser — including the secret token. Refactor me (see README.md).
import { use, useEffect, useState } from "react";

type Job = { id: number; title: string; company: string; description: string; saved: boolean };

export default function JobPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [job, setJob] = useState<Job | null>(null);
  const [saved, setSaved] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetch(`${process.env.API_URL}/api/v1/jobs/${id}`, { headers: { Authorization: `Bearer ${process.env.API_TOKEN}` } })
      .then((res) => res.json())
      .then((body) => {
        setJob(body.data);
        setSaved(body.data.saved);
      });
  }, [id]);

  if (!job) return <p>Loading…</p>;
  return (
    <article>
      <h1>{job.title}</h1>
      <p>{job.company}</p>
      {job.description.split(/\n\s*\n/).map((paragraph, i) => (
        <p key={i}>{paragraph}</p>
      ))}
      <button aria-pressed={saved} onClick={() => setSaved(!saved)}>{saved ? "Saved" : "Save job"}</button>
      <button
        onClick={async () => {
          await navigator.clipboard.writeText(`https://careerpilot.id/jobs/${id}`);
          setCopied(true);
        }}
      >
        {copied ? "Link copied" : "Copy link"}
      </button>
    </article>
  );
}

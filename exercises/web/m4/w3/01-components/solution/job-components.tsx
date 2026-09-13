import type { ReactNode } from "react";

export type Job = { id: number; title: string; company: string; city: string; salaryMax: number | null; skills: string[] };

const formatRupiah = (amount: number) => String(amount).replace(/\B(?=(\d{3})+(?!\d))/g, ".");

export function PageHeader({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <header>
      <h1>{title}</h1>
      {subtitle && <p>{subtitle}</p>}
    </header>
  );
}

export function JobCard({ job }: { job: Job }) {
  return (
    <article>
      <h2>{job.title}</h2>
      <p>
        {job.company} · {job.city}
      </p>
      <ul aria-label="Skills">
        {job.skills.map((skill) => (
          <li key={skill}>{skill}</li>
        ))}
      </ul>
      {job.salaryMax !== null && <p>Up to Rp {formatRupiah(job.salaryMax)}</p>}
    </article>
  );
}

export function EmptyState({ message, children }: { message: string; children?: ReactNode }) {
  return (
    <div role="status">
      <p>{message}</p>
      {children}
    </div>
  );
}

export function JobList({ jobs }: { jobs: Job[] }) {
  if (jobs.length === 0) return <EmptyState message="No jobs yet" />;
  return (
    <ul>
      {jobs.map((job) => (
        <li key={job.id}>
          <JobCard job={job} />
        </li>
      ))}
    </ul>
  );
}

export function JobsPage({ jobs }: { jobs: Job[] }) {
  return (
    <>
      <PageHeader title="Jobs for you" subtitle={`${jobs.length} open positions`} />
      <main>
        <JobList jobs={jobs} />
      </main>
    </>
  );
}

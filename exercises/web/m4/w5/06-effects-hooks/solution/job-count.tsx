// Derived data: just calculate it while rendering. No state, no effect, no extra render.
export function JobCount({ jobs, query }: { jobs: { title: string }[]; query: string }) {
  const needle = query.trim().toLowerCase();
  const count = needle ? jobs.filter((job) => job.title.toLowerCase().includes(needle)).length : jobs.length;
  return <p>{count} matching jobs</p>;
}

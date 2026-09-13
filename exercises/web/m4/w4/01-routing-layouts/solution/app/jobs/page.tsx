import Link from "next/link";
import { getJobs } from "../../lib/jobs-data";

export default async function JobsPage() {
  const jobs = await getJobs();
  return (
    <>
      <h1>Jobs</h1>
      <ul>
        {jobs.map((job) => (
          <li key={job.id}>
            <Link href={`/jobs/${job.id}`}>
              {job.title} · {job.company}
            </Link>
          </li>
        ))}
      </ul>
    </>
  );
}

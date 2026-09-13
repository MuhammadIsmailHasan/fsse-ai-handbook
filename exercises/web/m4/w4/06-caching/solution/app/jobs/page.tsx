import { cookies } from "next/headers";
import { Suspense } from "react";
import { getMyApplications } from "../../lib/applications";
import { getPublicJobs } from "../../lib/jobs";

export default function JobsPage() {
  return (
    <>
      <h1>Jobs</h1>
      {/* cached → part of the prerendered shell */}
      <JobList />
      {/* reads cookies at request time → streams in behind a fallback */}
      <Suspense fallback={<p role="status">Loading your applications…</p>}>
        <MyApplicationsSummary />
      </Suspense>
    </>
  );
}

export async function JobList() {
  const jobs = await getPublicJobs();
  return (
    <ul>
      {jobs.map((job) => (
        <li key={job.id}>{job.title}</li>
      ))}
    </ul>
  );
}

export async function MyApplicationsSummary() {
  const session = (await cookies()).get("session")?.value;
  if (!session) return <p>Log in to track applications</p>;
  const applications = await getMyApplications(session);
  return <p>You have {applications.length} applications</p>;
}

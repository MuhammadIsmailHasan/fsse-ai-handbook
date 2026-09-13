// Server Component: data + static markup on the server, interactive islands on the client.
import { notFound } from "next/navigation";
import { getJob } from "../../../lib/data";
import { JobDescription } from "./job-description";
import { SaveJobButton } from "./save-job-button";
import { ShareButton } from "./share-button";

export default async function JobPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const job = await getJob(Number(id));
  if (!job) notFound();

  return (
    <article>
      <h1>{job.title}</h1>
      <p>{job.company}</p>
      <JobDescription text={job.description} />
      <SaveJobButton jobId={job.id} initialSaved={job.saved} />
      <ShareButton url={`https://careerpilot.id/jobs/${job.id}`} />
    </article>
  );
}

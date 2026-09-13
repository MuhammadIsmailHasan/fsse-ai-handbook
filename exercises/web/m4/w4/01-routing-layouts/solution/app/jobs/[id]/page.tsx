import { notFound } from "next/navigation";
import { getJob } from "../../../lib/jobs-data";

export default async function JobPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!/^[1-9]\d*$/.test(id)) notFound();
  const job = await getJob(Number(id));
  if (!job) notFound();
  return (
    <>
      <h1>{job.title}</h1>
      <p>
        {job.company} · {job.city}
      </p>
    </>
  );
}

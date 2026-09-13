import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getJob } from "../../../lib/jobs-data";

type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const job = await getJob(Number(id));
  if (!job) return { title: "Job not found", robots: { index: false } };
  const description = `${job.title} at ${job.company} in ${job.city}`;
  return {
    title: job.title,
    description,
    alternates: { canonical: `/jobs/${id}` },
    openGraph: { title: job.title, description, url: `/jobs/${id}` },
  };
}

export default async function JobPage({ params }: Props) {
  const { id } = await params;
  const job = await getJob(Number(id)); // identical data calls in one request are cheap to repeat (memoized/cached)
  if (!job) notFound();
  return <h1>{job.title}</h1>;
}

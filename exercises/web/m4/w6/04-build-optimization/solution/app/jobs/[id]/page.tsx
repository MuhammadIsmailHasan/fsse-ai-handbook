import Image from "next/image";
import { notFound } from "next/navigation";
import { JobDescription } from "../../../components/job-description";
import { SalaryChartLazy } from "../../../components/salary-chart-lazy";
import { getJob } from "../../../lib/jobs";

export default async function JobPage({ params }: { params: Promise<{ id: string }> }) {
  const job = await getJob(Number((await params).id));
  if (!job) notFound();
  return (
    <article>
      {/* LCP element: preload it, and tell the browser it spans the viewport */}
      <Image src={job.bannerUrl} alt={`${job.title} at ${job.company}`} width={1200} height={400} sizes="100vw" preload />
      <header>
        <Image src={job.logoUrl} alt={`${job.company} logo`} width={64} height={64} />
        <h1>{job.title}</h1>
        <p>{job.company}</p>
      </header>
      <JobDescription markdown={job.description} />
      <SalaryChartLazy points={job.salaryPoints} />
    </article>
  );
}

import { notFound } from "next/navigation";
import { JobDescription } from "../../../components/job-description";
import SalaryChart from "../../../components/salary-chart";
import { getJob } from "../../../lib/jobs";

export default async function JobPage({ params }: { params: Promise<{ id: string }> }) {
  const job = await getJob(Number((await params).id));
  if (!job) notFound();
  return (
    <article>
      <img src={job.bannerUrl} />
      <header>
        <img src={job.logoUrl} alt="logo" />
        <h1>{job.title}</h1>
        <p>{job.company}</p>
      </header>
      <JobDescription markdown={job.description} />
      <SalaryChart points={job.salaryPoints} />
    </article>
  );
}

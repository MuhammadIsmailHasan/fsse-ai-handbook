import Link from "next/link";

export default function JobNotFound() {
  return (
    <>
      <h1>Job not found</h1>
      <Link href="/jobs">Back to jobs</Link>
    </>
  );
}

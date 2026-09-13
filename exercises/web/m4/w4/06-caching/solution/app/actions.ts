"use server";

import { updateTag } from "next/cache";
import { cookies } from "next/headers";

export async function closeJob(jobId: number): Promise<{ ok: boolean; message?: string }> {
  // Server Actions are public POST endpoints: always check who is calling.
  const session = (await cookies()).get("session")?.value;
  if (!session) return { ok: false, message: "Please log in" };

  const response = await fetch(`${process.env.API_URL}/api/v1/jobs/${jobId}/close`, {
    method: "POST",
    headers: { Authorization: `Bearer ${session}` },
  });
  if (!response.ok) return { ok: false, message: "Couldn't close the job" }; // expected error → return value

  updateTag("jobs"); // the user sees the change immediately (read-your-own-writes)
  updateTag(`job-${jobId}`);
  return { ok: true };
}

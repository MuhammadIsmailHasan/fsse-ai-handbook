// Provided: called from the browser. Talks to a Route Handler that forwards to the Flask API with the user's session.
export async function saveJob(jobId: number, saved: boolean): Promise<void> {
  const response = await fetch(`/api/saved-jobs/${jobId}`, { method: saved ? "PUT" : "DELETE" });
  if (!response.ok) throw new Error("Could not update saved job");
}

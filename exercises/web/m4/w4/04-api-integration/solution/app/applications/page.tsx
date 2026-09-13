import { redirect } from "next/navigation";
import { ApiError, type Status } from "../../lib/api-client";
import { getServerApi } from "../../lib/server-api";

const STATUSES: readonly Status[] = ["saved", "applied", "interview", "offer", "rejected"];

type Props = { searchParams: Promise<{ status?: string; page?: string }> };

export default async function ApplicationsPage({ searchParams }: Props) {
  const params = await searchParams;
  // Never trust the URL: validate before sending it to the API.
  const status = STATUSES.find((s) => s === params.status);
  const page = /^[1-9]\d*$/.test(params.page ?? "") ? Number(params.page) : 1;

  const api = await getServerApi();
  let result;
  try {
    result = await api.listApplications({ status, page: page === 1 ? undefined : page });
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) redirect("/login?next=/applications");
    throw error; // unexpected → nearest error.tsx
  }

  const totalPages = Math.max(1, Math.ceil(result.meta.total / result.meta.per_page));
  return (
    <>
      <h1>Applications</h1>
      {result.data.length === 0 ? (
        <p>No applications found</p>
      ) : (
        <>
          <ul>
            {result.data.map((application) => (
              <li key={application.id}>
                {application.role} at {application.company.name}
              </li>
            ))}
          </ul>
          <p>
            Page {result.meta.page} of {totalPages}
          </p>
        </>
      )}
    </>
  );
}

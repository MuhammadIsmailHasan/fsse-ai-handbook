import { forwardToFlask, readJson } from "../../../lib/bff";

export async function GET(request: Request) {
  const { search } = new URL(request.url);
  return forwardToFlask(`/api/v1/applications${search}`, { method: "GET" });
}

export async function POST(request: Request) {
  const body = await readJson(request);
  if (!body.ok) return body.response;
  return forwardToFlask("/api/v1/applications", { method: "POST", body: body.data });
}

import { forwardToFlask, readJson } from "../../../../lib/bff";

type Context = { params: Promise<{ id: string }> };

async function applicationPath(context: Context): Promise<string | null> {
  const { id } = await context.params;
  // Validate before building the upstream URL: "../users" must never reach Flask.
  return /^\d+$/.test(id) ? `/api/v1/applications/${id}` : null;
}

const invalidId = () => Response.json({ error: { code: "invalid_id" } }, { status: 400 });

export async function GET(_request: Request, context: Context) {
  const path = await applicationPath(context);
  return path ? forwardToFlask(path, { method: "GET" }) : invalidId();
}

export async function PATCH(request: Request, context: Context) {
  const path = await applicationPath(context);
  if (!path) return invalidId();
  const body = await readJson(request);
  if (!body.ok) return body.response;
  return forwardToFlask(path, { method: "PATCH", body: body.data });
}

export async function DELETE(_request: Request, context: Context) {
  const path = await applicationPath(context);
  return path ? forwardToFlask(path, { method: "DELETE" }) : invalidId();
}

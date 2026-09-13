import { getSession } from "./session";

const errorResponse = (status: number, code: string) => Response.json({ error: { code } }, { status });

export async function forwardToFlask(path: string, init: { method: string; body?: unknown }): Promise<Response> {
  const session = await getSession();
  if (!session) return errorResponse(401, "unauthenticated");

  const hasBody = init.body !== undefined;
  const headers: Record<string, string> = { Authorization: `Bearer ${session.accessToken}`, Accept: "application/json" };
  if (hasBody) headers["Content-Type"] = "application/json";

  let upstream: Response;
  try {
    upstream = await fetch(`${process.env.API_URL}${path}`, {
      method: init.method,
      headers,
      body: hasBody ? JSON.stringify(init.body) : undefined,
      cache: "no-store", // per-user data must never be cached
    });
  } catch {
    return errorResponse(502, "upstream_unavailable"); // details go to server logs, not to the browser
  }

  if (upstream.status === 204) return new Response(null, { status: 204 });
  return new Response(await upstream.text(), { status: upstream.status, headers: { "Content-Type": "application/json" } });
}

export async function readJson(request: Request): Promise<{ ok: true; data: unknown } | { ok: false; response: Response }> {
  try {
    return { ok: true, data: await request.json() };
  } catch {
    return { ok: false, response: errorResponse(400, "invalid_json") };
  }
}

// BFF helpers. See README.md.
export async function forwardToFlask(path: string, init: { method: string; body?: unknown }): Promise<Response> {
  throw new Error("TODO");
}

export async function readJson(request: Request): Promise<{ ok: true; data: unknown } | { ok: false; response: Response }> {
  throw new Error("TODO");
}

// Health check. See README.md.
export async function GET(): Promise<Response> {
  return new Response(null, { status: 501 });
}

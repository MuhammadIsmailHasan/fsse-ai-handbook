// GET + PATCH + DELETE /api/applications/:id. See README.md.
type Context = { params: Promise<{ id: string }> };

export async function GET(request: Request, context: Context): Promise<Response> {
  return new Response(null, { status: 501 });
}

export async function PATCH(request: Request, context: Context): Promise<Response> {
  return new Response(null, { status: 501 });
}

export async function DELETE(request: Request, context: Context): Promise<Response> {
  return new Response(null, { status: 501 });
}

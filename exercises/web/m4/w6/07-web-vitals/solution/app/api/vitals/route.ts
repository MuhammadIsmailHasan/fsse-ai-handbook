import { z } from "zod";

const MAX_BYTES = 2048;

const vitalSchema = z.object({
  name: z.enum(["LCP", "INP", "CLS", "FCP", "TTFB"]),
  value: z.number().nonnegative(),
  rating: z.enum(["good", "needs-improvement", "poor"]),
  id: z.string().max(100),
  navigationType: z.string().max(50).optional(),
  path: z.string().startsWith("/").max(200),
});

export async function POST(request: Request) {
  // Public, unauthenticated endpoint: keep it cheap and strict.
  if (Number(request.headers.get("content-length") ?? 0) > MAX_BYTES) return new Response(null, { status: 413 });

  let json: unknown;
  try {
    json = await request.json();
  } catch {
    return new Response(null, { status: 400 });
  }
  const parsed = vitalSchema.safeParse(json);
  if (!parsed.success) return new Response(null, { status: 400 });

  console.info(JSON.stringify({ event: "web_vital", ...parsed.data }));
  return new Response(null, { status: 204 });
}

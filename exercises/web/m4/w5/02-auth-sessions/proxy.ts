// Optimistic route protection. See README.md.
import { NextResponse, type NextRequest } from "next/server";

export default async function proxy(request: NextRequest) {
  return NextResponse.next();
}

export const config = { matcher: ["/:path*"] };

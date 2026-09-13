import { NextResponse, type NextRequest } from "next/server";
import { decrypt } from "./lib/session";

const PROTECTED_PREFIXES = ["/dashboard", "/applications"];

const matchesPrefix = (path: string, prefix: string) => path === prefix || path.startsWith(`${prefix}/`);

export default async function proxy(request: NextRequest) {
  const { pathname, search } = request.nextUrl;
  // Optimistic: read the cookie only (no database/API calls — proxy runs on every request).
  const session = await decrypt(request.cookies.get("session")?.value);

  if (PROTECTED_PREFIXES.some((prefix) => matchesPrefix(pathname, prefix)) && !session) {
    const loginUrl = new URL("/login", request.nextUrl);
    loginUrl.searchParams.set("next", `${pathname}${search}`);
    return NextResponse.redirect(loginUrl);
  }

  if (matchesPrefix(pathname, "/login") && session) {
    return NextResponse.redirect(new URL("/dashboard", request.nextUrl));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};

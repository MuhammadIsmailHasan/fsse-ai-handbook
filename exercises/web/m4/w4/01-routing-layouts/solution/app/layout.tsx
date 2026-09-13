import Link from "next/link";
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header>
          <nav aria-label="Main">
            <Link href="/jobs">Jobs</Link> <Link href="/dashboard">Dashboard</Link>
          </nav>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}

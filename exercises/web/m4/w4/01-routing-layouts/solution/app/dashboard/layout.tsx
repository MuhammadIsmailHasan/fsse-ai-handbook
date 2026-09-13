import Link from "next/link";
import type { ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div>
      <aside aria-label="Dashboard">
        <Link href="/dashboard">Overview</Link> <Link href="/dashboard/applications">Applications</Link>
      </aside>
      <section>{children}</section>
    </div>
  );
}

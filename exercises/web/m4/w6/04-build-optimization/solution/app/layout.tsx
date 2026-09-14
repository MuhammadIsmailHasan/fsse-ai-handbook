import { Inter } from "next/font/google";
import type { ReactNode } from "react";

// Downloaded at build time and served from our own domain; size-adjusted fallback avoids layout shift.
const inter = Inter({ subsets: ["latin"], display: "swap", variable: "--font-sans" });

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body style={{ fontFamily: "var(--font-sans), sans-serif" }}>{children}</body>
    </html>
  );
}

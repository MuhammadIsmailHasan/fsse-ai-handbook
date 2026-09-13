import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  metadataBase: new URL("https://careerpilot.id"), // relative URLs below become absolute
  title: { default: "CareerPilot", template: "%s · CareerPilot" },
  description: "Track job applications, see what the market wants, and prepare for interviews with AI.",
  openGraph: { siteName: "CareerPilot", locale: "id_ID", type: "website" },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

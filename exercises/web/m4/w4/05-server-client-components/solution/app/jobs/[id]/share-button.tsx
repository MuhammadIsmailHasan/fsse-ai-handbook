"use client";

import { useState } from "react";

export function ShareButton({ url }: { url: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      type="button"
      onClick={async () => {
        await navigator.clipboard.writeText(url); // browser-only API → Client Component
        setCopied(true);
      }}
    >
      {copied ? "Link copied" : "Copy link"}
    </button>
  );
}

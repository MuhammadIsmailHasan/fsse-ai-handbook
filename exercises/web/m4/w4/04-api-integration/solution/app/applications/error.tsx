"use client"; // error boundaries must be Client Components

import { useEffect } from "react";

export default function ApplicationsError({ error, retry }: { error: Error & { digest?: string }; retry: () => void }) {
  useEffect(() => {
    console.error(error); // send to error monitoring (e.g. Sentry) in production
  }, [error]);

  return (
    <div role="alert">
      <h2>We couldn&apos;t load your applications</h2>
      <button type="button" onClick={() => retry()}>
        Try again
      </button>
    </div>
  );
}

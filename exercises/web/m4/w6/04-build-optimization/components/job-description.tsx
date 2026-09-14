"use client";

import { useState } from "react";
import { renderMarkdown } from "../lib/markdown";

export function JobDescription({ markdown }: { markdown: string }) {
  const [html] = useState(() => renderMarkdown(markdown));
  return <div className="prose" dangerouslySetInnerHTML={{ __html: html }} />;
}

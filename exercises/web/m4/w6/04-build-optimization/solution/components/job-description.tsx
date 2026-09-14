import { renderMarkdown } from "../lib/markdown";

// Server Component: the parser runs on the server and never reaches the browser bundle.
export function JobDescription({ markdown }: { markdown: string }) {
  return <div className="prose" dangerouslySetInnerHTML={{ __html: renderMarkdown(markdown) }} />;
}

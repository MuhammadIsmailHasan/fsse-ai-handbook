// Server Component: pure formatting, zero client JavaScript.
export function JobDescription({ text }: { text: string }) {
  return (
    <>
      {text
        .split(/\n\s*\n/)
        .map((paragraph) => paragraph.trim())
        .filter(Boolean)
        .map((paragraph, index) => (
          <p key={index}>{paragraph}</p>
        ))}
    </>
  );
}

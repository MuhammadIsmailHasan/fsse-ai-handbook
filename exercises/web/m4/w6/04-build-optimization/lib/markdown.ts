// Provided. Pretend this is a 90 KB markdown parser.
import "server-only";

const escapeHtml = (text: string) => text.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]!);

export function renderMarkdown(markdown: string): string {
  return markdown
    .split(/\n{2,}/)
    .map((block) => {
      const inline = (s: string) => escapeHtml(s).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
      if (block.split("\n").every((line) => line.startsWith("- "))) {
        return `<ul>${block.split("\n").map((line) => `<li>${inline(line.slice(2))}</li>`).join("")}</ul>`;
      }
      return `<p>${inline(block)}</p>`;
    })
    .join("");
}

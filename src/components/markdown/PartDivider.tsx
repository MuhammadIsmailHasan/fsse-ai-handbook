/**
 * PartDivider.tsx — a clear band between the 3 parts of a lesson.
 *
 * Markdown:  ::part[Learn the Concept]{n="1"}
 */
export function PartDivider({ n, label }: { n?: string; label?: string }) {
  return (
    <div className="not-prose my-12 flex items-center gap-4" role="separator">
      <span className="h-px flex-1 bg-gradient-to-r from-transparent to-indigo-300 dark:to-indigo-500/50" />
      <span className="rounded-full border border-indigo-200 bg-indigo-50 px-4 py-1 text-xs font-bold tracking-widest text-indigo-700 uppercase dark:border-indigo-500/30 dark:bg-indigo-500/10 dark:text-indigo-300">
        {n ? `Part ${n} · ` : ''}
        {label}
      </span>
      <span className="h-px flex-1 bg-gradient-to-l from-transparent to-indigo-300 dark:to-indigo-500/50" />
    </div>
  )
}

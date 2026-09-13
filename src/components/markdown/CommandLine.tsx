/**
 * CommandLine.tsx — a terminal command with a copy button.
 */
import { CopyButton } from '../ui/CopyButton'

export function CommandLine({ command }: { command: string }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-lg bg-slate-900 px-3 py-2 font-mono text-xs text-slate-100 dark:bg-black/40">
      {/* A <span>, not <code>: lesson styles give inline <code> a light background. */}
      <span className="overflow-x-auto whitespace-nowrap">
        <span className="text-slate-500 select-none">$ </span>
        {command}
      </span>
      <CopyButton
        text={command}
        className="shrink-0 rounded px-2 py-0.5 font-sans text-xs text-slate-400 hover:bg-slate-700 hover:text-white"
      />
    </div>
  )
}

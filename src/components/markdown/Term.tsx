/**
 * Term.tsx — a key term with its Bahasa Indonesia explanation.
 *
 * Markdown:  :term[Middleware]{bahasa="perantara — kode yang berjalan di antara request dan route"}
 *
 * Teaches: accessible tooltips. The explanation appears on hover AND on keyboard
 * focus (tabIndex=0), and screen readers get it via `aria-describedby`.
 */
import { useId, type ReactNode } from 'react'

export function Term({ bahasa, children }: { bahasa?: string; children?: ReactNode }) {
  const tooltipId = useId()

  if (!bahasa) return <strong>{children}</strong>

  return (
    <span className="group relative inline-block">
      <span
        tabIndex={0}
        aria-describedby={tooltipId}
        className="cursor-help font-semibold text-slate-900 underline decoration-rose-400 decoration-dotted underline-offset-4 dark:text-white"
      >
        {children}
      </span>
      <span
        id={tooltipId}
        role="tooltip"
        className="pointer-events-none invisible absolute bottom-full left-1/2 z-20 mb-2 w-64 -translate-x-1/2 rounded-lg bg-slate-900 px-3 py-2 text-sm leading-snug font-normal text-white opacity-0 shadow-lg transition group-focus-within:visible group-focus-within:opacity-100 group-hover:visible group-hover:opacity-100 dark:bg-slate-700"
      >
        🇮🇩 {bahasa}
      </span>
    </span>
  )
}

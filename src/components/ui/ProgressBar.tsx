/**
 * ProgressBar.tsx — an accessible progress bar.
 *
 * Teaches: ARIA roles. A styled <div> means nothing to a screen reader;
 * `role="progressbar"` + aria-value* attributes make it understandable.
 */
export function ProgressBar({ percent, label }: { percent: number; label: string }) {
  return (
    <div
      role="progressbar"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={percent}
      className="h-1.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800"
    >
      <div
        className="h-full rounded-full bg-indigo-500 transition-[width] duration-300"
        style={{ width: `${percent}%` }}
      />
    </div>
  )
}

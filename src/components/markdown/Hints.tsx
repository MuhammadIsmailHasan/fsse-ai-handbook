/**
 * Hints.tsx — hints revealed one at a time.
 *
 * Markdown:
 *   :::hints
 *   - First hint
 *   - Second hint
 *   :::
 *
 * Teaches: `Children.toArray` to work with a component's children as an array,
 * and deriving what to show from a single number in state.
 */
import { Children, isValidElement, useState, type ReactNode } from 'react'

export function Hints({ title, children }: { title?: string; children?: ReactNode }) {
  return (
    <div className="not-prose my-6 rounded-xl border border-dashed border-slate-300 p-4 dark:border-slate-700">
      <p className="mb-2 font-semibold text-slate-900 dark:text-white">💡 {title ?? 'Hints'}</p>
      {children}
    </div>
  )
}

export function HintList({ children }: { children?: ReactNode }) {
  // react-markdown adds "\n" text between list items — keep only real elements.
  const items = Children.toArray(children).filter(isValidElement)
  const [shown, setShown] = useState(0)

  return (
    <div className="space-y-2">
      <ol className="space-y-2">
        {items.slice(0, shown).map((item, index) => (
          <li
            key={index}
            className="rounded-lg bg-slate-50 px-3 py-2 text-slate-700 dark:bg-slate-900 dark:text-slate-300"
          >
            <span className="mr-2 font-semibold text-slate-500">#{index + 1}</span>
            {item}
          </li>
        ))}
      </ol>
      {shown < items.length ? (
        <button
          type="button"
          onClick={() => setShown((count) => count + 1)}
          className="rounded-lg bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
        >
          Show hint {shown + 1} of {items.length}
        </button>
      ) : (
        <p className="text-sm text-slate-500">All hints shown. You've got this!</p>
      )}
    </div>
  )
}

/** Each list item: render its content inline (the <li> comes from HintList). */
export function HintItem({ children }: { children?: ReactNode }) {
  return <span className="[&>p]:inline">{children}</span>
}

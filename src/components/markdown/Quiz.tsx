/**
 * Quiz.tsx — a question with a hidden answer.
 *
 * Markdown:
 *   :::quiz
 *   What does HTTP stand for?
 *
 *   HyperText Transfer Protocol — the rules browsers and servers use to talk.
 *   :::
 *
 * (The first paragraph is the question; everything after it is the answer.)
 */
import { useState, type ReactNode } from 'react'
import { useLocale } from '../../hooks/useLocale'

export function Quiz({ children }: { children?: ReactNode }) {
  return (
    <div className="my-5 rounded-xl border border-slate-200 px-5 py-3 dark:border-slate-800">
      {children}
    </div>
  )
}

export function QuizQuestion({ children }: { children?: ReactNode }) {
  return (
    <div className="flex gap-2 font-medium text-slate-900 dark:text-white">
      <span aria-hidden="true" className="mt-[0.2em]">
        ❓
      </span>
      <div className="[&>p]:my-0">{children}</div>
    </div>
  )
}

export function QuizAnswer({ children }: { children?: ReactNode }) {
  const [open, setOpen] = useState(false)
  const { t } = useLocale()

  return (
    <div className="mt-2">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
        className="not-prose text-sm font-medium text-indigo-600 hover:underline dark:text-indigo-400"
      >
        {open ? t('quiz.hide') : t('quiz.show')}
      </button>
      {open && (
        <div className="mt-2 rounded-lg bg-slate-50 px-4 py-1 dark:bg-slate-900">{children}</div>
      )}
    </div>
  )
}

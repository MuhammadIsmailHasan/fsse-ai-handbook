/**
 * PlacementCheck.tsx — "Do I already know this week?" self-assessment.
 *
 * Markdown (outer fence uses 4 colons so quizzes can be nested inside):
 *   ::::placement{id="modules/m1/w0"}
 *   Try these without notes or AI…
 *   :::quiz
 *   …
 *   :::
 *   ::::
 */
import type { ReactNode } from 'react'
import { useStudy } from '../../hooks/useStudy'

export function PlacementCheck({ id, children }: { id?: string; children?: ReactNode }) {
  const { placements, setPlacement } = useStudy()
  const result = id ? placements[id] : undefined

  return (
    <section className="my-8 rounded-xl border-2 border-amber-200 px-5 py-4 dark:border-amber-500/30">
      <p className="not-prose font-semibold text-slate-900 dark:text-white">✅ Placement check</p>
      <p className="not-prose mt-1 text-sm text-slate-600 dark:text-slate-400">
        Answer from memory — no notes, no AI. Be honest: this only helps you.
      </p>

      <div className="mt-2">{children}</div>

      {id && (
        <div className="not-prose mt-4 border-t border-amber-200 pt-4 dark:border-amber-500/30">
          {result ? (
            <div className="flex flex-wrap items-center gap-3 text-sm" role="status">
              <span className="font-medium">
                {result.result === 'pass'
                  ? '🎉 Passed — jump to the toy exercises and skim the rest.'
                  : '📚 Studying this week — no problem, that is what it is for.'}
              </span>
              <button
                type="button"
                onClick={() => setPlacement(id, null)}
                className="text-slate-500 underline hover:text-slate-800 dark:hover:text-slate-200"
              >
                Retake
              </button>
            </div>
          ) : (
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => setPlacement(id, 'pass')}
                className="rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700"
              >
                I could answer everything well
              </button>
              <button
                type="button"
                onClick={() => setPlacement(id, 'study')}
                className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800"
              >
                Not yet — I'll study this week
              </button>
            </div>
          )}
        </div>
      )}
    </section>
  )
}

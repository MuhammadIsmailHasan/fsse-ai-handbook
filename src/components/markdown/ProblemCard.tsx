/**
 * ProblemCard.tsx — a DSA practice problem that joins the spaced review queue once solved.
 *
 * Markdown:
 *   :::problem{id="dsa-pair-sum" title="Pair With Target Sum" difficulty="easy" path="exercises/dsa/..."}
 *   Problem description…
 *   :::
 */
import type { ReactNode } from 'react'
import { useLocation } from 'react-router'
import { useStudy } from '../../hooks/useStudy'
import type { ProblemDifficulty } from '../../lib/spaced-repetition'
import { exerciseRunner } from '../../lib/exercise-commands'
import { CommandLine } from './CommandLine'

const DIFFICULTY: Record<ProblemDifficulty, string> = {
  easy: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-500/15 dark:text-emerald-300',
  medium: 'bg-amber-100 text-amber-800 dark:bg-amber-500/15 dark:text-amber-300',
  hard: 'bg-red-100 text-red-800 dark:bg-red-500/15 dark:text-red-300',
}

function isDifficulty(value: string | undefined): value is ProblemDifficulty {
  return value === 'easy' || value === 'medium' || value === 'hard'
}

type ProblemCardProps = {
  id?: string
  title?: string
  difficulty?: string
  path?: string
  children?: ReactNode
}

export function ProblemCard({
  id,
  title = 'Problem',
  difficulty,
  path,
  children,
}: ProblemCardProps) {
  const { pathname } = useLocation()
  const { reviewQueue, addToReview } = useStudy()
  const level = isDifficulty(difficulty) ? difficulty : undefined
  const item = id ? reviewQueue[id] : undefined

  return (
    <section className="my-6 rounded-xl border border-slate-200 px-5 py-4 dark:border-slate-800">
      <header className="not-prose flex flex-wrap items-center gap-2">
        <span aria-hidden="true">🧩</span>
        <p className="font-semibold text-slate-900 dark:text-white">{title}</p>
        {level && (
          <span
            className={`rounded-full px-2 py-0.5 text-xs font-semibold capitalize ${DIFFICULTY[level]}`}
          >
            {level}
          </span>
        )}
      </header>

      <div>{children}</div>

      <div className="not-prose mt-3 space-y-3">
        {path && <CommandLine command={exerciseRunner(path).command} />}

        {id &&
          (item ? (
            <p className="text-sm text-slate-600 dark:text-slate-400" role="status">
              {item.mastered
                ? '🏆 Mastered — reviewed at every interval.'
                : `🔁 In your review queue · next review ${item.nextDue}`}
            </p>
          ) : (
            <button
              type="button"
              onClick={() => addToReview({ id, title, lessonUrl: pathname, difficulty: level })}
              className="rounded-lg bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-700"
            >
              ✅ I solved it — schedule reviews
            </button>
          ))}
      </div>
    </section>
  )
}

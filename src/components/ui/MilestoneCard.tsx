/**
 * MilestoneCard.tsx — one job-ready milestone with core-lesson progress.
 */
import { allLessons } from '../../content'
import { milestoneProgress } from '../../content/planning'
import { useStudy } from '../../hooks/useStudy'
import type { Course } from '../../types/content'
import { ProgressBar } from './ProgressBar'

export function MilestoneCard({ milestone }: { milestone: Course['milestones'][number] }) {
  const { completed, targetRole } = useStudy()
  const progress = milestoneProgress(milestone, allLessons, completed, targetRole)

  return (
    <article className="rounded-xl border border-slate-200 p-5 dark:border-slate-800">
      <h3 className="font-semibold text-slate-900 dark:text-white">{milestone.title}</h3>
      <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">{milestone.applyFor}</p>
      <p className="mt-1 text-xs text-slate-500">{milestone.estimate}</p>
      <div className="mt-4 flex items-center gap-3">
        <ProgressBar percent={progress.percent} label={`${milestone.title} progress`} />
        <span className="shrink-0 text-xs text-slate-500 tabular-nums">
          {progress.total === 0 ? 'content coming' : `${progress.done}/${progress.total} core`}
        </span>
      </div>
    </article>
  )
}

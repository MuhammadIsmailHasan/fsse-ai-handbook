/**
 * MilestoneCard.tsx — one job-ready milestone with core-lesson progress.
 */
import { milestoneProgress } from '../../content/planning'
import { useContent } from '../../hooks/useContent'
import { useLocale } from '../../hooks/useLocale'
import { useStudy } from '../../hooks/useStudy'
import type { Course } from '../../types/content'
import { ProgressBar } from './ProgressBar'

export function MilestoneCard({ milestone }: { milestone: Course['milestones'][number] }) {
  const { completed, targetRole } = useStudy()
  const { allLessons } = useContent()
  const { t } = useLocale()
  const progress = milestoneProgress(milestone, allLessons, completed, targetRole)

  return (
    <article className="rounded-xl border border-slate-200 p-5 dark:border-slate-800">
      <h3 className="font-semibold text-slate-900 dark:text-white">{milestone.title}</h3>
      <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">{milestone.applyFor}</p>
      <p className="mt-1 text-xs text-slate-500">{milestone.estimate}</p>
      <div className="mt-4 flex items-center gap-3">
        <ProgressBar
          percent={progress.percent}
          label={t('list.progress', { title: milestone.title })}
        />
        <span className="shrink-0 text-xs text-slate-500 tabular-nums">
          {progress.total === 0
            ? t('milestones.comingContent')
            : t('targetRole.core', { done: progress.done, total: progress.total })}
        </span>
      </div>
    </article>
  )
}

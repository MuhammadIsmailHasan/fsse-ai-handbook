/**
 * MilestoneCard.tsx — one job-ready milestone: core progress and WHEN you could apply.
 *
 * The date estimate uses two paces: your daily target (Settings) and, once there is
 * enough history, the time you actually logged. Seeing both keeps the plan honest.
 */
import { milestoneProgress, milestonesRemaining } from '../../content/planning'
import { useContent } from '../../hooks/useContent'
import { useLocale } from '../../hooks/useLocale'
import { useStudy } from '../../hooks/useStudy'
import { estimateFinish, weeklyPace } from '../../lib/study-time'
import type { Course } from '../../types/content'
import { ProgressBar } from './ProgressBar'

export function MilestoneCard({ milestone }: { milestone: Course['milestones'][number] }) {
  const { completed, targetRole, studyGoal, studyLog } = useStudy()
  const { allLessons, course } = useContent()
  const { t, formatDuration, formatNumber, intlLocale } = useLocale()
  const progress = milestoneProgress(milestone, allLessons, completed, targetRole)

  const today = new Date()
  const remaining = milestonesRemaining(course.milestones, allLessons, completed).find(
    (item) => item.id === milestone.id,
  )!
  const pace = weeklyPace(studyLog, studyGoal, today)
  const monthYear = new Intl.DateTimeFormat(intlLocale, { month: 'short', year: 'numeric' })

  function etaText(weeklyMinutes: number) {
    const eta = estimateFinish(remaining.remainingMin, remaining.remainingMax, weeklyMinutes, today)
    if (!eta) return null
    const from = monthYear.format(eta.from)
    const to = monthYear.format(eta.to)
    const when = from === to ? from : `${from} – ${to}`
    if (eta.monthsMax < 1) return t('milestones.etaSoon', { when })
    const low = Math.max(1, Math.round(eta.monthsMin))
    const high = Math.max(low, Math.round(eta.monthsMax))
    const months = low === high ? formatNumber(low) : `${formatNumber(low)}–${formatNumber(high)}`
    return t('milestones.eta', { months, when })
  }

  return (
    <article className="flex flex-col rounded-xl border border-slate-200 p-5 dark:border-slate-800">
      <h3 className="font-semibold text-slate-900 dark:text-white">{milestone.title}</h3>
      <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">{milestone.applyFor}</p>
      <p className="mt-1 text-xs text-slate-500">
        {t('milestones.hours', { min: milestone.hours.min, max: milestone.hours.max })}
      </p>

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

      <dl className="mt-4 space-y-2 border-t border-slate-100 pt-3 text-sm dark:border-slate-800">
        {remaining.remainingMax === 0 ? (
          <p className="font-medium text-emerald-700 dark:text-emerald-400">
            {t('milestones.ready')}
          </p>
        ) : (
          <>
            <div>
              <dt className="text-xs text-slate-500">
                {t('milestones.etaTarget', { weekly: formatDuration(pace.target) })}
              </dt>
              <dd className="font-medium text-slate-900 dark:text-white">
                📅 {etaText(pace.target)}
              </dd>
            </div>
            {pace.recent !== null ? (
              <div>
                <dt className="text-xs text-slate-500">
                  {t('milestones.etaRecent', { weekly: formatDuration(pace.recent) })}
                </dt>
                <dd className="font-medium text-slate-900 dark:text-white">
                  🏃 {etaText(pace.recent) ?? '—'}
                </dd>
              </div>
            ) : (
              <p className="text-xs text-slate-500">{t('milestones.noPace')}</p>
            )}
          </>
        )}
      </dl>
    </article>
  )
}

/**
 * DashboardPage.tsx — the home page: where you are and what to do next.
 */
import { Link } from 'react-router'
import { MilestoneCard } from '../components/ui/MilestoneCard'
import { PageHeader } from '../components/ui/PageHeader'
import { orderedStream, pickForBudget } from '../content/planning'
import { useContent } from '../hooks/useContent'
import { useLocale } from '../hooks/useLocale'
import { useStudy } from '../hooks/useStudy'
import { targetRoleLabel } from '../lib/roles'
import { dueItems } from '../lib/spaced-repetition'
import { dateKey } from '../lib/study-time'

export function DashboardPage() {
  const { completed, targetRole, reviewQueue, studyLog, studyGoal } = useStudy()
  const { allLessons, course, getLesson } = useContent()
  const { t, formatDuration } = useLocale()
  const next = pickForBudget(
    orderedStream(course.studyPath.module, allLessons),
    completed,
    targetRole,
    1,
  )[0]
  const due = dueItems(reviewQueue, new Date()).length
  const doneCount = Object.keys(completed).filter((id) => getLesson(id)).length
  const guide = getLesson('guides/how-to-study')

  return (
    <div className="mx-auto max-w-5xl">
      <PageHeader
        eyebrow={`🎯 ${targetRoleLabel(targetRole)}`}
        title={t('dashboard.title')}
        description={t('dashboard.description')}
      />

      <div className="grid gap-4 md:grid-cols-3">
        <Link
          to={next?.url ?? '/roadmap'}
          className="rounded-xl bg-indigo-600 p-5 text-white shadow-sm hover:bg-indigo-700 md:col-span-2"
        >
          <p className="text-sm text-indigo-100">{t('dashboard.continue')}</p>
          <p className="mt-1 text-xl font-semibold">{next?.title ?? t('dashboard.openRoadmap')}</p>
          {next && <p className="mt-1 line-clamp-2 text-sm text-indigo-100">{next.summary}</p>}
        </Link>

        <div className="grid gap-4">
          <Stat
            to="/schedule"
            label={t('dashboard.today')}
            value={`⏱️ ${formatDuration(studyLog[dateKey(new Date())] ?? 0)} / ${formatDuration(studyGoal.targetMinutes)}`}
          />
          <Stat to="/tracks/dsa/review" label={t('dashboard.reviewsDue')} value={`🔁 ${due}`} />
          <Stat to="/roadmap" label={t('dashboard.lessonsDone')} value={`✅ ${doneCount}`} />
        </div>
      </div>

      {guide && !completed[guide.id] && (
        <Link
          to={guide.url}
          className="mt-4 block rounded-xl border border-dashed border-slate-300 px-5 py-3 text-sm hover:border-indigo-400 dark:border-slate-700"
        >
          {t('dashboard.newHereBefore')} <strong>{guide.title}</strong>{' '}
          {t('dashboard.newHereAfter')}
        </Link>
      )}

      <h2 className="mt-12 mb-4 text-xl font-bold text-slate-900 dark:text-white">
        {t('milestones.heading')}
      </h2>
      <div className="grid gap-4 md:grid-cols-3">
        {course.milestones.map((milestone) => (
          <MilestoneCard key={milestone.id} milestone={milestone} />
        ))}
      </div>
    </div>
  )
}

function Stat({ to, label, value }: { to: string; label: string; value: string }) {
  return (
    <Link
      to={to}
      className="flex items-center justify-between rounded-xl border border-slate-200 px-4 py-3 hover:border-indigo-400 dark:border-slate-800"
    >
      <span className="text-sm text-slate-600 dark:text-slate-400">{label}</span>
      <span className="font-semibold text-slate-900 dark:text-white">{value}</span>
    </Link>
  )
}

/**
 * SchedulePage.tsx — "This Week": a plan built from your progress and target role.
 *
 * Teaches: turning a written study routine (3 h/day, 6 days) into numbers
 * (minutes per stream) and letting a small algorithm fill each stream.
 */
import { Link } from 'react-router'
import { PageHeader } from '../components/ui/PageHeader'
import { orderedStream, pickForBudget } from '../content/planning'
import { useContent } from '../hooks/useContent'
import { useLocale } from '../hooks/useLocale'
import { useStudy } from '../hooks/useStudy'
import { dueItems } from '../lib/spaced-repetition'
import type { LessonMeta } from '../types/content'

/** Weekly minutes per stream, from the default routine in docs/IMPLEMENTATION_PLAN.md §13. */
const WEEKLY_BUDGET = {
  module: 5 * 120, // Mon–Fri: 2 h module lesson
  dsa: 5 * 60, // Mon–Fri: 1 h DSA
  architecture: 90, // Sat: 1.5 h
  project: 90, // Sat: 1.5 h
} as const

// Text is stored as message keys, translated when rendered.
const STREAMS = [
  { key: 'module', title: 'schedule.streamModule', when: 'schedule.whenModule' },
  { key: 'dsa', title: 'schedule.streamDsa', when: 'schedule.whenDsa' },
  { key: 'architecture', title: 'schedule.streamArchitecture', when: 'schedule.whenSaturday' },
  { key: 'project', title: 'schedule.streamProject', when: 'schedule.whenSaturday' },
] as const

const ROUTINE = [
  { day: 'schedule.monFri', plan: 'schedule.routineWeekday' },
  { day: 'schedule.saturday', plan: 'schedule.routineSaturday' },
  { day: 'schedule.sunday', plan: 'schedule.routineSunday' },
] as const

export function SchedulePage() {
  const { completed, targetRole, reviewQueue } = useStudy()
  const due = dueItems(reviewQueue, new Date()).length
  const { allLessons, course } = useContent()
  const { t } = useLocale()

  return (
    <div className="mx-auto max-w-4xl">
      <PageHeader
        eyebrow={t('schedule.eyebrow')}
        title={t('schedule.title')}
        description={t('schedule.description')}
      />

      <section className="mb-8 overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800">
        <table className="w-full text-left text-sm">
          <tbody>
            {ROUTINE.map((row) => (
              <tr
                key={row.day}
                className="border-b border-slate-100 last:border-0 dark:border-slate-800"
              >
                <th className="w-32 px-4 py-2.5 font-medium text-slate-900 dark:text-white">
                  {t(row.day)}
                </th>
                <td className="px-4 py-2.5 text-slate-600 dark:text-slate-400">{t(row.plan)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {due > 0 && (
        <Link
          to="/tracks/dsa/review"
          className="mb-8 block rounded-xl border border-amber-300 bg-amber-50 px-5 py-3 text-sm font-medium text-amber-900 dark:border-amber-500/40 dark:bg-amber-500/10 dark:text-amber-200"
        >
          {due === 1 ? t('schedule.dueOne') : t('schedule.dueMany', { count: due })}
        </Link>
      )}

      <div className="grid gap-5 md:grid-cols-2">
        {STREAMS.map((stream) => {
          const lessons = pickForBudget(
            orderedStream(course.studyPath[stream.key], allLessons),
            completed,
            targetRole,
            WEEKLY_BUDGET[stream.key],
          )
          return (
            <StreamCard
              key={stream.key}
              title={t(stream.title)}
              when={t(stream.when)}
              lessons={lessons}
            />
          )
        })}
      </div>
    </div>
  )
}

function StreamCard(props: { title: string; when: string; lessons: LessonMeta[] }) {
  const minutes = props.lessons.reduce((sum, lesson) => sum + lesson.durationMinutes, 0)
  const { t, formatNumber } = useLocale()
  const hours = (m: number) => formatNumber(Math.round((m / 60) * 10) / 10)

  return (
    <section className="rounded-xl border border-slate-200 p-5 dark:border-slate-800">
      <div className="flex items-baseline justify-between gap-2">
        <h2 className="font-semibold text-slate-900 dark:text-white">{props.title}</h2>
        <span className="text-xs text-slate-500">{props.when}</span>
      </div>
      {props.lessons.length === 0 ? (
        <p className="mt-3 text-sm text-slate-400 italic">{t('schedule.nothingPlanned')}</p>
      ) : (
        <>
          <ol className="mt-3 space-y-2">
            {props.lessons.map((lesson) => (
              <li key={lesson.id}>
                <Link
                  to={lesson.url}
                  className="block rounded-lg px-3 py-2 hover:bg-slate-50 dark:hover:bg-slate-900"
                >
                  <span className="block text-sm font-medium text-slate-900 dark:text-white">
                    {lesson.title}
                  </span>
                  <span className="text-xs text-slate-500">
                    {t('schedule.hours', { hours: hours(lesson.durationMinutes) })}
                  </span>
                </Link>
              </li>
            ))}
          </ol>
          <p className="mt-3 text-xs text-slate-500">
            {t('schedule.planned', { hours: hours(minutes) })}
          </p>
        </>
      )}
    </section>
  )
}

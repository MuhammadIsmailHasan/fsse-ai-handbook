/**
 * SchedulePage.tsx — "This Week": a plan built from your progress and target role.
 *
 * Teaches: turning a written study routine (3 h/day, 6 days) into numbers
 * (minutes per stream) and letting a small algorithm fill each stream.
 */
import { Link } from 'react-router'
import { PageHeader } from '../components/ui/PageHeader'
import { allLessons, course } from '../content'
import { orderedStream, pickForBudget } from '../content/planning'
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

const STREAMS = [
  { key: 'module', title: '📘 Module lessons', when: 'Mon–Fri · 2 h/day' },
  { key: 'dsa', title: '🧩 DSA', when: 'Mon–Fri · 1 h/day' },
  { key: 'architecture', title: '🏛️ Architecture', when: 'Saturday · 1.5 h' },
  { key: 'project', title: '⭐ Project', when: 'Saturday · 1.5 h' },
] as const

const ROUTINE = [
  { day: 'Mon–Fri', plan: '2 h module lesson + 1 h DSA' },
  { day: 'Saturday', plan: '1.5 h Architecture + 1.5 h CareerPilot' },
  { day: 'Sunday', plan: 'Light: DSA spaced review + weekly LinkedIn post, or rest' },
]

export function SchedulePage() {
  const { completed, targetRole, reviewQueue } = useStudy()
  const due = dueItems(reviewQueue, new Date()).length

  return (
    <div className="mx-auto max-w-4xl">
      <PageHeader
        eyebrow="Overview"
        title="This Week"
        description="Your next lessons, picked in the recommended order and sized to ~18 hours. Only 🟢 Core and 🔵 Recommended lessons for your target role are included."
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
                  {row.day}
                </th>
                <td className="px-4 py-2.5 text-slate-600 dark:text-slate-400">{row.plan}</td>
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
          🔁 {due} DSA problem{due === 1 ? '' : 's'} due for review →
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
              title={stream.title}
              when={stream.when}
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

  return (
    <section className="rounded-xl border border-slate-200 p-5 dark:border-slate-800">
      <div className="flex items-baseline justify-between gap-2">
        <h2 className="font-semibold text-slate-900 dark:text-white">{props.title}</h2>
        <span className="text-xs text-slate-500">{props.when}</span>
      </div>
      {props.lessons.length === 0 ? (
        <p className="mt-3 text-sm text-slate-400 italic">
          Nothing planned — all done here, or content is still being written.
        </p>
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
                    ~{Math.round((lesson.durationMinutes / 60) * 10) / 10} h
                  </span>
                </Link>
              </li>
            ))}
          </ol>
          <p className="mt-3 text-xs text-slate-500">
            Planned: ~{Math.round((minutes / 60) * 10) / 10} h
          </p>
        </>
      )}
    </section>
  )
}

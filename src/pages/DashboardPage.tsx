/**
 * DashboardPage.tsx — the home page: where you are and what to do next.
 */
import { Link } from 'react-router'
import { MilestoneCard } from '../components/ui/MilestoneCard'
import { PageHeader } from '../components/ui/PageHeader'
import { allLessons, course, getLesson } from '../content'
import { orderedStream, pickForBudget } from '../content/planning'
import { useStudy } from '../hooks/useStudy'
import { TARGET_ROLES } from '../lib/roles'
import { dueItems } from '../lib/spaced-repetition'

export function DashboardPage() {
  const { completed, targetRole, reviewQueue } = useStudy()
  const role = TARGET_ROLES.find((r) => r.id === targetRole)!
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
        eyebrow={`🎯 ${role.label}`}
        title="Welcome back 👋"
        description="Small steps every day beat big weekends. Here's where you are."
      />

      <div className="grid gap-4 md:grid-cols-3">
        <Link
          to={next?.url ?? '/roadmap'}
          className="rounded-xl bg-indigo-600 p-5 text-white shadow-sm hover:bg-indigo-700 md:col-span-2"
        >
          <p className="text-sm text-indigo-100">Continue learning</p>
          <p className="mt-1 text-xl font-semibold">{next?.title ?? 'Open the roadmap'}</p>
          {next && <p className="mt-1 line-clamp-2 text-sm text-indigo-100">{next.summary}</p>}
        </Link>

        <div className="grid gap-4">
          <Stat to="/schedule" label="This week's plan" value="📅 Open" />
          <Stat to="/tracks/dsa/review" label="DSA reviews due" value={`🔁 ${due}`} />
          <Stat to="/roadmap" label="Lessons done" value={`✅ ${doneCount}`} />
        </div>
      </div>

      {guide && !completed[guide.id] && (
        <Link
          to={guide.url}
          className="mt-4 block rounded-xl border border-dashed border-slate-300 px-5 py-3 text-sm hover:border-indigo-400 dark:border-slate-700"
        >
          📖 New here? Read <strong>{guide.title}</strong> first (10 minutes).
        </Link>
      )}

      <h2 className="mt-12 mb-4 text-xl font-bold text-slate-900 dark:text-white">
        Job-ready milestones
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

/**
 * RoadmapPage.tsx — the whole course at a glance: modules, tracks, projects, milestones.
 */
import { Link } from 'react-router'
import { MilestoneCard } from '../components/ui/MilestoneCard'
import { PageHeader } from '../components/ui/PageHeader'
import { ProgressBar } from '../components/ui/ProgressBar'
import { RoleBadges } from '../components/ui/RoleBadges'
import { course, getLessonsInGroup } from '../content'
import { countProgress } from '../content/progress'
import { useStudy } from '../hooks/useStudy'

export function RoadmapPage() {
  const { completed } = useStudy()

  return (
    <div className="mx-auto max-w-5xl space-y-12">
      <PageHeader
        eyebrow="Overview"
        title="Roadmap"
        description="Eight modules in order, two tracks alongside them, and projects that grow with you. You can start applying for jobs at Milestone 1."
      />

      <section>
        <h2 className="mb-4 text-xl font-bold text-slate-900 dark:text-white">
          Job-ready milestones
        </h2>
        <div className="grid gap-4 md:grid-cols-3">
          {course.milestones.map((milestone) => (
            <MilestoneCard key={milestone.id} milestone={milestone} />
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-4 text-xl font-bold text-slate-900 dark:text-white">Modules</h2>
        <div className="grid gap-4 md:grid-cols-2">
          {course.modules.map((module) => {
            const progress = countProgress(getLessonsInGroup('modules', module.id), completed)
            return (
              <Link
                key={module.id}
                to={`/modules/${module.id}`}
                className="rounded-xl border border-slate-200 p-5 hover:border-indigo-400 dark:border-slate-800 dark:hover:border-indigo-500"
              >
                <p className="text-xs font-medium text-indigo-600 dark:text-indigo-400">
                  Module {module.number} ·{' '}
                  {module.source === 'original' ? '🔥 Bonus' : '📘 the bootcamp outline'}
                  {module.source === 'mixed' ? ' + 🔥' : ''}
                </p>
                <h3 className="mt-1 font-semibold text-slate-900 dark:text-white">
                  {module.title}
                </h3>
                <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">{module.summary}</p>
                <div className="mt-3">
                  <RoleBadges roles={module.roles} />
                </div>
                <div className="mt-4 flex items-center gap-3">
                  <ProgressBar percent={progress.percent} label={`${module.title} progress`} />
                  <span className="shrink-0 text-xs text-slate-500 tabular-nums">
                    {progress.total ? `${progress.done}/${progress.total}` : 'coming soon'}
                  </span>
                </div>
              </Link>
            )
          })}
        </div>
      </section>

      <section className="grid gap-8 md:grid-cols-2">
        <div>
          <h2 className="mb-4 text-xl font-bold text-slate-900 dark:text-white">Parallel tracks</h2>
          <div className="space-y-3">
            {course.tracks.map((track) => (
              <Link
                key={track.id}
                to={`/tracks/${track.id}`}
                className="block rounded-xl border border-slate-200 p-4 hover:border-indigo-400 dark:border-slate-800"
              >
                <h3 className="font-semibold text-slate-900 dark:text-white">{track.title}</h3>
                <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">{track.summary}</p>
              </Link>
            ))}
          </div>
        </div>
        <div>
          <h2 className="mb-4 text-xl font-bold text-slate-900 dark:text-white">Projects</h2>
          <div className="space-y-3">
            {course.projects.map((project) => (
              <Link
                key={project.id}
                to={`/projects/${project.id}`}
                className="block rounded-xl border border-slate-200 p-4 hover:border-indigo-400 dark:border-slate-800"
              >
                <h3 className="font-semibold text-slate-900 dark:text-white">{project.title}</h3>
                <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">{project.tagline}</p>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}

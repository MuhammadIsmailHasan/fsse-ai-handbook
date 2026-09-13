/**
 * SectionedLessonList.tsx — lessons grouped by week/stage, used on overview pages.
 *
 * Teaches: reusing one component for modules, tracks and projects by passing
 * plain data (`sections`) instead of hard-coding where the data comes from.
 */
import { Link } from 'react-router'
import { countProgress, isVisibleForRole } from '../../content/progress'
import { useStudy } from '../../hooks/useStudy'
import { levelFor } from '../../lib/roles'
import type { LessonMeta } from '../../types/content'
import { Icon } from '../ui/Icon'
import { LevelDot } from '../ui/LevelDot'
import { ProgressBar } from '../ui/ProgressBar'

export type LessonSection = {
  id: string
  title: string
  summary?: string
  note?: string
  lessons: LessonMeta[]
}

export function SectionedLessonList({ sections }: { sections: LessonSection[] }) {
  const { completed, targetRole, hideNotNeeded } = useStudy()

  return (
    <div className="space-y-6">
      {sections.map((section) => {
        const progress = countProgress(section.lessons, completed)
        const visible = section.lessons.filter((lesson) =>
          isVisibleForRole(lesson, targetRole, hideNotNeeded),
        )

        return (
          <section
            key={section.id}
            className="rounded-xl border border-slate-200 p-5 dark:border-slate-800"
          >
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <h2 className="font-semibold text-slate-900 dark:text-white">{section.title}</h2>
                {section.summary && (
                  <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
                    {section.summary}
                  </p>
                )}
                {section.note && <p className="mt-1 text-xs text-slate-400">{section.note}</p>}
              </div>
              {progress.total > 0 && (
                <span className="text-xs text-slate-500 tabular-nums">
                  {progress.done}/{progress.total} done
                </span>
              )}
            </div>

            {progress.total > 0 && (
              <div className="mt-3">
                <ProgressBar percent={progress.percent} label={`${section.title} progress`} />
              </div>
            )}

            {section.lessons.length === 0 ? (
              <p className="mt-3 text-sm text-slate-400 italic">Content coming soon.</p>
            ) : (
              <ul className="mt-4 divide-y divide-slate-100 dark:divide-slate-800/70">
                {visible.map((lesson) => (
                  <li key={lesson.id}>
                    <Link
                      to={lesson.url}
                      className="flex items-center gap-3 py-2.5 hover:text-indigo-700 dark:hover:text-indigo-300"
                    >
                      {completed[lesson.id] ? (
                        <Icon name="check" size={14} className="shrink-0 text-emerald-500" />
                      ) : (
                        <LevelDot level={levelFor(lesson.roles, targetRole)} />
                      )}
                      <span className="min-w-0 flex-1">
                        <span className="block text-sm font-medium">{lesson.title}</span>
                        <span className="block truncate text-xs text-slate-500">
                          {lesson.summary}
                        </span>
                      </span>
                      <span className="hidden shrink-0 text-xs text-slate-400 sm:inline">
                        {lesson.source === 'original' ? '🔥 Bonus · ' : ''}~
                        {Math.round((lesson.durationMinutes / 60) * 10) / 10} h
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </section>
        )
      })}
    </div>
  )
}

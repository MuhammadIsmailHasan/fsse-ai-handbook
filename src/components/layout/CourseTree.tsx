/**
 * CourseTree.tsx — the collapsible Module → Week → Lesson tree in the sidebar.
 *
 * Teaches:
 * - Deriving UI state instead of syncing it: a group is open if the user opened it
 *   OR it contains the current page. No effect needed to "auto-open" anything.
 * - Recursive-ish composition: the same <TreeGroup> renders modules, tracks and projects.
 */
import { useState } from 'react'
import { NavLink, useLocation } from 'react-router'
import { allLessons, course } from '../../content'
import { countProgress, isVisibleForRole } from '../../content/progress'
import { useStudy } from '../../hooks/useStudy'
import { levelFor } from '../../lib/roles'
import type { LessonMeta } from '../../types/content'
import { Icon } from '../ui/Icon'
import { LevelDot } from '../ui/LevelDot'

type Section = { id: string | null; title: string; lessons: LessonMeta[] }

type TreeGroupProps = {
  id: string
  label: string
  to: string
  sections: Section[]
  onNavigate: () => void
}

export function CourseTree({ onNavigate }: { onNavigate: () => void }) {
  return (
    <ul className="space-y-0.5">
      {course.modules.map((module) => (
        <li key={module.id}>
          <TreeGroup
            id={`modules/${module.id}`}
            label={`${module.number} · ${module.title}`}
            to={`/modules/${module.id}`}
            sections={module.weeks.map((week) => ({
              id: week.id,
              title: week.title,
              lessons: lessonsIn('modules', module.id, week.id),
            }))}
            onNavigate={onNavigate}
          />
        </li>
      ))}
    </ul>
  )
}

export function TrackTree({ onNavigate }: { onNavigate: () => void }) {
  return (
    <ul className="space-y-0.5">
      {course.tracks.map((track) => (
        <li key={track.id}>
          <TreeGroup
            id={`tracks/${track.id}`}
            label={track.title}
            to={`/tracks/${track.id}`}
            sections={track.stages.map((stage) => ({
              id: stage.id,
              title: stage.title,
              lessons: lessonsIn('tracks', track.id, stage.id),
            }))}
            onNavigate={onNavigate}
          />
        </li>
      ))}
    </ul>
  )
}

export function ProjectTree({ onNavigate }: { onNavigate: () => void }) {
  return (
    <ul className="space-y-0.5">
      {course.projects.map((project) => (
        <li key={project.id}>
          <TreeGroup
            id={`projects/${project.id}`}
            label={project.title}
            to={`/projects/${project.id}`}
            sections={[{ id: null, title: '', lessons: lessonsIn('projects', project.id, null) }]}
            onNavigate={onNavigate}
          />
        </li>
      ))}
    </ul>
  )
}

function lessonsIn(collection: LessonMeta['collection'], group: string, section: string | null) {
  return allLessons.filter(
    (l) => l.collection === collection && l.group === group && l.section === section,
  )
}

function TreeGroup({ id, label, to, sections, onNavigate }: TreeGroupProps) {
  const { pathname } = useLocation()
  const { completed, targetRole, hideNotNeeded } = useStudy()
  // `undefined` = the user hasn't toggled it → fall back to "open if I'm inside it".
  const [userOpen, setUserOpen] = useState<boolean | undefined>(undefined)

  const containsCurrentPage = pathname === `/${id}` || pathname.startsWith(`/${id}/`)
  const open = userOpen ?? containsCurrentPage

  const allInGroup = sections.flatMap((section) => section.lessons)
  const progress = countProgress(allInGroup, completed)

  return (
    <div>
      <div className="flex items-center">
        <button
          type="button"
          onClick={() => setUserOpen(!open)}
          aria-expanded={open}
          aria-label={`${open ? 'Collapse' : 'Expand'} ${label}`}
          className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-slate-200"
        >
          <Icon name={open ? 'chevronDown' : 'chevronRight'} size={14} />
        </button>
        <NavLink
          to={to}
          end
          onClick={onNavigate}
          className={({ isActive }) =>
            `flex min-w-0 flex-1 items-center justify-between gap-2 rounded-md px-1.5 py-1 text-sm ${
              isActive
                ? 'font-medium text-indigo-700 dark:text-indigo-300'
                : 'text-slate-700 hover:text-slate-950 dark:text-slate-300 dark:hover:text-white'
            }`
          }
        >
          <span className="truncate">{label}</span>
          {progress.total > 0 && (
            <span className="shrink-0 text-[0.7rem] text-slate-400 tabular-nums">
              {progress.done}/{progress.total}
            </span>
          )}
        </NavLink>
      </div>

      {open && (
        <div className="mt-0.5 mb-2 ml-3 border-l border-slate-200 pl-2 dark:border-slate-800">
          {allInGroup.length === 0 && (
            <p className="px-2 py-1 text-xs text-slate-400 italic">Content coming soon</p>
          )}
          {sections.map((section) => {
            const visible = section.lessons.filter((lesson) =>
              isVisibleForRole(lesson, targetRole, hideNotNeeded),
            )
            if (visible.length === 0) return null
            return (
              <div key={section.id ?? 'all'} className="mb-1">
                {section.title && (
                  <p className="px-2 pt-1.5 pb-0.5 text-[0.7rem] font-semibold tracking-wide text-slate-400 uppercase">
                    {section.title}
                  </p>
                )}
                <ul>
                  {visible.map((lesson) => (
                    <li key={lesson.id}>
                      <NavLink
                        to={lesson.url}
                        onClick={onNavigate}
                        className={({ isActive }) =>
                          `flex items-center gap-2 rounded-md px-2 py-1 text-[0.8rem] leading-snug ${
                            isActive
                              ? 'bg-indigo-50 font-medium text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-300'
                              : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800/60'
                          }`
                        }
                      >
                        {completed[lesson.id] ? (
                          <Icon name="check" size={12} className="shrink-0 text-emerald-500" />
                        ) : (
                          <LevelDot level={levelFor(lesson.roles, targetRole)} />
                        )}
                        <span className="min-w-0">{lesson.title}</span>
                      </NavLink>
                    </li>
                  ))}
                </ul>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

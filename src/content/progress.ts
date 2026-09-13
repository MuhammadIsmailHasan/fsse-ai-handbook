/**
 * progress.ts — pure functions that count progress.
 *
 * Teaches: `reduce`-free counting with `filter().length`, and designing functions
 * that take plain data (no hooks) so they work anywhere and are easy to test.
 */
import type { TargetRole } from '../lib/roles'
import { levelFor } from '../lib/roles'
import type { LessonMeta } from '../types/content'

export type ProgressCount = { done: number; total: number; percent: number }

export function countProgress(
  lessons: LessonMeta[],
  completed: Record<string, string>,
): ProgressCount {
  const total = lessons.length
  const done = lessons.filter((lesson) => completed[lesson.id]).length
  return { done, total, percent: total === 0 ? 0 : Math.round((done / total) * 100) }
}

/** Progress on the lessons that are 🟢 Core for the target role. */
export function countCoreProgress(
  lessons: LessonMeta[],
  completed: Record<string, string>,
  target: TargetRole,
): ProgressCount {
  const core = lessons.filter((lesson) => levelFor(lesson.roles, target) === 'core')
  return countProgress(core, completed)
}

/** Should this lesson appear in lists, given the "hide not needed" preference? */
export function isVisibleForRole(lesson: LessonMeta, target: TargetRole, hideNotNeeded: boolean) {
  return !hideNotNeeded || levelFor(lesson.roles, target) !== 'none'
}

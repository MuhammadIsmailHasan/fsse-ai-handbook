/**
 * planning.ts — milestone progress and "what should I study this week?"
 *
 * Teaches:
 * - Prefix matching as a tiny query language ("modules/m1" matches every M1 lesson).
 * - A greedy algorithm: keep taking the next lesson until the weekly time budget is used.
 *   (You'll meet greedy algorithms again in the DSA track.)
 */
import { levelFor, type TargetRole } from '../lib/roles'
import type { Course, LessonMeta } from '../types/content'
import { countProgress, type ProgressCount } from './progress'

export const matchesPrefix = (lessonId: string, prefix: string) =>
  lessonId === prefix || lessonId.startsWith(prefix.endsWith('/') ? prefix : `${prefix}/`) ||
  // project pages are matched by number prefix, e.g. "projects/careerpilot/01"
  (/\/\d+$/.test(prefix) && lessonId.startsWith(`${prefix}-`))

/** Lessons that are Core or Recommended for the role — the ones a plan should include. */
export function isPlanned(lesson: LessonMeta, target: TargetRole) {
  const level = levelFor(lesson.roles, target)
  return level === 'core' || level === 'recommended'
}

export function milestoneProgress(
  milestone: Course['milestones'][number],
  lessons: LessonMeta[],
  completed: Record<string, string>,
  target: TargetRole,
): ProgressCount {
  const inScope = lessons.filter(
    (lesson) =>
      levelFor(lesson.roles, target) === 'core' &&
      milestone.include.some((prefix) => matchesPrefix(lesson.id, prefix)),
  )
  return countProgress(inScope, completed)
}

/** Lessons of one stream, in the recommended order. */
export function orderedStream(prefixes: string[], lessons: LessonMeta[]): LessonMeta[] {
  const seen = new Set<string>()
  const result: LessonMeta[] = []
  for (const prefix of prefixes) {
    for (const lesson of lessons) {
      if (!seen.has(lesson.id) && matchesPrefix(lesson.id, prefix)) {
        seen.add(lesson.id)
        result.push(lesson)
      }
    }
  }
  return result
}

/** Greedy: take unfinished planned lessons in order until the minutes budget is used. */
export function pickForBudget(
  stream: LessonMeta[],
  completed: Record<string, string>,
  target: TargetRole,
  budgetMinutes: number,
): LessonMeta[] {
  const picked: LessonMeta[] = []
  let used = 0
  for (const lesson of stream) {
    if (completed[lesson.id] || !isPlanned(lesson, target)) continue
    // Always pick at least one lesson, even if it is longer than the budget.
    if (picked.length > 0 && used + lesson.durationMinutes > budgetMinutes) break
    picked.push(lesson)
    used += lesson.durationMinutes
  }
  return picked
}

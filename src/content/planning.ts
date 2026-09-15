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

export type MilestoneRemaining = {
  id: string
  /** Hours of finished lessons that belong to this milestone. */
  doneHours: number
  /** Hours still to study to reach this milestone, INCLUDING earlier milestones. */
  remainingMin: number
  remainingMax: number
}

/**
 * How many study hours are left until each milestone.
 *
 * Milestones are steps: reaching #2 means finishing #1 first, so the remaining hours add up.
 * The hour ranges in course.json include exercises and projects, so we subtract only the
 * lessons you've marked done (each lesson counted once, in the first milestone that lists it).
 */
export function milestonesRemaining(
  milestones: Course['milestones'],
  lessons: LessonMeta[],
  completed: Record<string, string>,
): MilestoneRemaining[] {
  const counted = new Set<string>()
  let carryMin = 0
  let carryMax = 0
  return milestones.map((milestone) => {
    let doneMinutes = 0
    for (const lesson of lessons) {
      if (counted.has(lesson.id)) continue
      if (!milestone.include.some((prefix) => matchesPrefix(lesson.id, prefix))) continue
      counted.add(lesson.id)
      if (completed[lesson.id]) doneMinutes += lesson.durationMinutes
    }
    const doneHours = doneMinutes / 60
    carryMin += Math.max(0, milestone.hours.min - doneHours)
    carryMax += Math.max(0, milestone.hours.max - doneHours)
    return {
      id: milestone.id,
      doneHours: Math.round(doneHours),
      remainingMin: Math.round(carryMin),
      remainingMax: Math.round(carryMax),
    }
  })
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

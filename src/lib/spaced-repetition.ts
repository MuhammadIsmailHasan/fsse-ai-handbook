/**
 * spaced-repetition.ts — schedule DSA problems for review so you don't forget them.
 *
 * The idea: review something right before you'd forget it. Each successful review
 * pushes the next one further away (1 → 3 → 7 → 14 → 30 days). If you forgot,
 * start again from 1 day.
 *
 * Teaches:
 * - Pure functions with an explicit `today` parameter → deterministic tests
 *   (no hidden `new Date()` inside).
 * - Returning NEW objects instead of mutating inputs (immutability).
 * - Working with calendar dates as "YYYY-MM-DD" strings in LOCAL time.
 */

export const INTERVALS_DAYS = [1, 3, 7, 14, 30] as const

export type ProblemDifficulty = 'easy' | 'medium' | 'hard'
export type ReviewOutcome = 'remembered' | 'forgot'

export type ReviewItem = {
  id: string
  title: string
  lessonUrl: string
  difficulty?: ProblemDifficulty
  /** Index into INTERVALS_DAYS for the NEXT review. */
  step: number
  nextDue: string
  addedAt: string
  reviews: number
  mastered: boolean
}

export type ReviewQueue = Record<string, ReviewItem>

/** Local calendar date as "YYYY-MM-DD" (not UTC — "today" should mean YOUR today). */
export function toDateKey(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function addDays(dateKey: string, days: number): string {
  const [year, month, day] = dateKey.split('-').map(Number)
  return toDateKey(new Date(year!, month! - 1, day! + days))
}

export function addToQueue(
  queue: ReviewQueue,
  problem: Pick<ReviewItem, 'id' | 'title' | 'lessonUrl' | 'difficulty'>,
  today: Date,
): ReviewQueue {
  if (queue[problem.id]) return queue // already scheduled
  const todayKey = toDateKey(today)
  return {
    ...queue,
    [problem.id]: {
      ...problem,
      step: 0,
      nextDue: addDays(todayKey, INTERVALS_DAYS[0]),
      addedAt: todayKey,
      reviews: 0,
      mastered: false,
    },
  }
}

export function recordReview(item: ReviewItem, outcome: ReviewOutcome, today: Date): ReviewItem {
  const todayKey = toDateKey(today)

  if (outcome === 'forgot') {
    return {
      ...item,
      step: 0,
      nextDue: addDays(todayKey, INTERVALS_DAYS[0]),
      reviews: item.reviews + 1,
    }
  }

  const nextStep = item.step + 1
  if (nextStep >= INTERVALS_DAYS.length) {
    return { ...item, step: nextStep, reviews: item.reviews + 1, mastered: true }
  }
  return {
    ...item,
    step: nextStep,
    nextDue: addDays(todayKey, INTERVALS_DAYS[nextStep]!),
    reviews: item.reviews + 1,
  }
}

export function dueItems(queue: ReviewQueue, today: Date): ReviewItem[] {
  const todayKey = toDateKey(today)
  return Object.values(queue)
    .filter((item) => !item.mastered && item.nextDue <= todayKey) // "YYYY-MM-DD" sorts correctly as text
    .sort((a, b) => a.nextDue.localeCompare(b.nextDue))
}

export function upcomingItems(queue: ReviewQueue, today: Date): ReviewItem[] {
  const todayKey = toDateKey(today)
  return Object.values(queue)
    .filter((item) => !item.mastered && item.nextDue > todayKey)
    .sort((a, b) => a.nextDue.localeCompare(b.nextDue))
}

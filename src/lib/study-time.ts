/**
 * study-time.ts — flexible daily study goals: target, minimum, and what actually happened.
 *
 * Real life: some days you have 5 hours, some days 45 minutes. So the app keeps
 * three numbers instead of one fixed plan:
 * - a TARGET (the day you hope for),
 * - a MINIMUM (the small day that still counts),
 * - a LOG of minutes you really studied — and plans today from the time you really have.
 *
 * Teaches: keeping date/time logic in pure functions (dates passed in, never `new Date()`
 * inside), so every rule is easy to test.
 */

export type StudyGoal = {
  /** The day you hope for, in minutes (e.g. 300 = 5 h). */
  targetMinutes: number
  /** The smallest day that still counts, in minutes. */
  minimumMinutes: number
  /** Study days per week: Mon–Fri (5), + Saturday (6), + Sunday (7). */
  studyDays: 5 | 6 | 7
}

/** "YYYY-MM-DD" (local date) → minutes studied that day. */
export type StudyLog = Record<string, number>

export type Stream = 'module' | 'dsa' | 'architecture' | 'project'

export const DEFAULT_GOAL: StudyGoal = { targetMinutes: 300, minimumMinutes: 60, studyDays: 6 }

/** Limits for stored values (data from localStorage may be old or edited by hand). */
export function normalizeGoal(value: Partial<StudyGoal> | undefined): StudyGoal {
  const clamp = (n: unknown, min: number, max: number, fallback: number) =>
    typeof n === 'number' && Number.isFinite(n)
      ? Math.min(max, Math.max(min, Math.round(n)))
      : fallback
  const targetMinutes = clamp(value?.targetMinutes, 30, 720, DEFAULT_GOAL.targetMinutes)
  const minimumMinutes = clamp(
    value?.minimumMinutes,
    15,
    targetMinutes,
    Math.min(60, targetMinutes),
  )
  const studyDays = value?.studyDays === 5 || value?.studyDays === 7 ? value.studyDays : 6
  return { targetMinutes, minimumMinutes, studyDays }
}

/** Local calendar date as "YYYY-MM-DD" (not UTC — 01:00 in Jakarta is still "today"). */
export function dateKey(date: Date): string {
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

/** Monday of the week containing `date`, at local midnight. */
export function startOfWeek(date: Date): Date {
  const monday = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  monday.setDate(monday.getDate() - ((monday.getDay() + 6) % 7))
  return monday
}

/** The 7 days (Mon → Sun) of the week containing `date`. */
export function weekDates(date: Date): Date[] {
  const monday = startOfWeek(date)
  return Array.from({ length: 7 }, (_, i) => {
    const day = new Date(monday)
    day.setDate(monday.getDate() + i)
    return day
  })
}

/** 0 = Monday … 6 = Sunday */
const weekdayIndex = (date: Date) => (date.getDay() + 6) % 7

export function isStudyDay(date: Date, goal: StudyGoal): boolean {
  return weekdayIndex(date) < goal.studyDays
}

export type DaySummary = {
  date: string
  minutes: number
  isStudyDay: boolean
  metMinimum: boolean
  metTarget: boolean
  isToday: boolean
  isFuture: boolean
}

export function summarizeWeek(log: StudyLog, goal: StudyGoal, today: Date) {
  const todayKey = dateKey(today)
  const days: DaySummary[] = weekDates(today).map((day) => {
    const key = dateKey(day)
    const minutes = log[key] ?? 0
    return {
      date: key,
      minutes,
      isStudyDay: isStudyDay(day, goal),
      metMinimum: minutes >= goal.minimumMinutes,
      metTarget: minutes >= goal.targetMinutes,
      isToday: key === todayKey,
      isFuture: key > todayKey,
    }
  })
  return {
    days,
    totalMinutes: days.reduce((sum, day) => sum + day.minutes, 0),
    targetMinutes: goal.targetMinutes * goal.studyDays,
    /** Study days so far (today included) that reached the minimum. */
    daysAtMinimum: days.filter((d) => d.isStudyDay && !d.isFuture && d.metMinimum).length,
    studyDaysSoFar: days.filter((d) => d.isStudyDay && !d.isFuture).length,
  }
}

/**
 * Average minutes per study day over the last `days` days (today excluded, it isn't over),
 * counting only from the first day you logged — so a new user isn't dragged down by zeros.
 * Returns null when there is no history yet.
 */
export function recentAverage(
  log: StudyLog,
  goal: StudyGoal,
  today: Date,
  days = 14,
): number | null {
  return recentStats(log, goal, today, days)?.minutes ?? null
}

/** Like recentAverage, but also says how many study days the average is based on. */
export function recentStats(
  log: StudyLog,
  goal: StudyGoal,
  today: Date,
  days = 14,
): { minutes: number; days: number } | null {
  const logged = Object.keys(log)
    .filter((key) => (log[key] ?? 0) > 0)
    .sort()
  if (logged.length === 0) return null
  const firstLogged = logged[0]!
  let total = 0
  let count = 0
  for (let i = 1; i <= days; i++) {
    const day = new Date(today.getFullYear(), today.getMonth(), today.getDate() - i)
    const key = dateKey(day)
    if (key < firstLogged) break
    if (!isStudyDay(day, goal)) continue
    total += log[key] ?? 0
    count++
  }
  return count === 0 ? null : { minutes: Math.round(total / count), days: count }
}

/**
 * Weekly study minutes two ways: the TARGET pace, and the RECENT real pace
 * (only with at least `minDays` study days of history — a couple of days says little).
 */
export function weeklyPace(log: StudyLog, goal: StudyGoal, today: Date, minDays = 5) {
  const recent = recentStats(log, goal, today)
  return {
    target: goal.targetMinutes * goal.studyDays,
    recent: recent && recent.days >= minDays ? recent.minutes * goal.studyDays : null,
  }
}

const WEEKS_PER_MONTH = 52 / 12

/** When will `minHours`–`maxHours` of study be done at `weeklyMinutes` per week? */
export function estimateFinish(
  minHours: number,
  maxHours: number,
  weeklyMinutes: number,
  today: Date,
) {
  if (weeklyMinutes <= 0) return null
  const weeks = (hours: number) => (hours * 60) / weeklyMinutes
  const dateAfter = (w: number) =>
    new Date(today.getFullYear(), today.getMonth(), today.getDate() + Math.ceil(w * 7))
  return {
    monthsMin: weeks(minHours) / WEEKS_PER_MONTH,
    monthsMax: weeks(maxHours) / WEEKS_PER_MONTH,
    from: dateAfter(weeks(minHours)),
    to: dateAfter(weeks(maxHours)),
  }
}

/** How a day's time is shared between the study streams. */
const DAY_MIX: Record<'weekday' | 'saturday' | 'sunday', [Stream, number][]> = {
  weekday: [
    ['module', 0.65],
    ['dsa', 0.35],
  ],
  saturday: [
    ['architecture', 0.5],
    ['project', 0.5],
  ],
  sunday: [
    ['module', 0.5],
    ['dsa', 0.5],
  ],
}

const MIN_BLOCK = 20
const roundTo5 = (n: number) => Math.round(n / 5) * 5

export type TimeBlock = { stream: Stream; minutes: number }

/**
 * Splits the time you have TODAY into blocks. Tiny blocks (< 20 min) aren't worth
 * switching topics for, so they're merged into the main block.
 */
export function planDay(availableMinutes: number, date: Date): TimeBlock[] {
  const total = roundTo5(Math.max(0, availableMinutes))
  if (total === 0) return []
  const index = weekdayIndex(date)
  const mix = DAY_MIX[index === 5 ? 'saturday' : index === 6 ? 'sunday' : 'weekday']

  const blocks = mix.map(([stream, share]) => ({ stream, minutes: roundTo5(total * share) }))
  const [main, ...others] = blocks as [TimeBlock, ...TimeBlock[]]
  const kept = others.filter((block) => block.minutes >= MIN_BLOCK)
  // Whatever isn't in a kept block (small blocks + rounding) goes to the main block.
  main.minutes = total - kept.reduce((sum, block) => sum + block.minutes, 0)
  return [main, ...kept]
}

/** Minutes per stream for a whole week at the target pace. */
export function weeklyBudget(goal: StudyGoal, today: Date): Record<Stream, number> {
  const budget: Record<Stream, number> = { module: 0, dsa: 0, architecture: 0, project: 0 }
  for (const day of weekDates(today)) {
    if (!isStudyDay(day, goal)) continue
    for (const block of planDay(goal.targetMinutes, day)) budget[block.stream] += block.minutes
  }
  return budget
}

/** Whole minutes between two timestamps, capped so a forgotten timer can't log a whole day. */
export function elapsedMinutes(startIso: string, now: Date, capMinutes = 8 * 60): number {
  const start = Date.parse(startIso)
  if (Number.isNaN(start)) return 0
  return Math.min(capMinutes, Math.max(0, Math.floor((now.getTime() - start) / 60_000)))
}

/** Adds (or with a negative number, removes) minutes for one day. Never below 0. */
export function addMinutes(log: StudyLog, key: string, delta: number): StudyLog {
  const minutes = Math.max(0, Math.min(24 * 60, (log[key] ?? 0) + Math.round(delta)))
  const next = { ...log }
  if (minutes === 0) delete next[key]
  else next[key] = minutes
  return next
}

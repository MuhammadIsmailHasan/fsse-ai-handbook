import { describe, expect, it } from 'vitest'
import {
  addMinutes,
  dateKey,
  elapsedMinutes,
  estimateFinish,
  normalizeGoal,
  planDay,
  recentAverage,
  summarizeWeek,
  weekDates,
  weeklyBudget,
  weeklyPace,
  type StudyGoal,
} from './study-time'

const goal: StudyGoal = { targetMinutes: 300, minimumMinutes: 60, studyDays: 6 }
// Wednesday 17 Sep 2025, local time
const wednesday = new Date(2025, 8, 17, 21, 30)

describe('dates', () => {
  it('uses the local calendar date', () => {
    expect(dateKey(new Date(2025, 0, 5, 0, 30))).toBe('2025-01-05')
  })

  it('builds Monday-to-Sunday weeks', () => {
    const days = weekDates(wednesday).map(dateKey)
    expect(days[0]).toBe('2025-09-15')
    expect(days[6]).toBe('2025-09-21')
    expect(weekDates(new Date(2025, 8, 21)).map(dateKey)[0]).toBe('2025-09-15') // Sunday
  })
})

describe('normalizeGoal', () => {
  it('fills defaults and keeps the minimum below the target', () => {
    expect(normalizeGoal(undefined)).toEqual({
      targetMinutes: 300,
      minimumMinutes: 60,
      studyDays: 6,
    })
    expect(normalizeGoal({ targetMinutes: 45, minimumMinutes: 90, studyDays: 7 })).toEqual({
      targetMinutes: 45,
      minimumMinutes: 45,
      studyDays: 7,
    })
  })
})

describe('summarizeWeek', () => {
  it('counts totals and days that reached the minimum so far', () => {
    const log = { '2025-09-15': 300, '2025-09-16': 40, '2025-09-17': 90, '2025-09-14': 500 }
    const week = summarizeWeek(log, goal, wednesday)
    expect(week.totalMinutes).toBe(430) // last Sunday is not this week
    expect(week.targetMinutes).toBe(1800)
    expect(week.daysAtMinimum).toBe(2)
    expect(week.studyDaysSoFar).toBe(3)
    expect(week.days[0]!.metTarget).toBe(true)
    expect(week.days[2]!.isToday).toBe(true)
    expect(week.days[6]!.isStudyDay).toBe(false)
  })
})

describe('recentAverage', () => {
  it('returns null without history', () => {
    expect(recentAverage({}, goal, wednesday)).toBeNull()
  })

  it('averages study days since the first log, excluding today and rest days', () => {
    // Fri 12: 120, Sat 13: 60, Sun 14: 600 (rest day), Mon 15: 180, Tue 16: 0, today: 300
    const log = {
      '2025-09-12': 120,
      '2025-09-13': 60,
      '2025-09-14': 600,
      '2025-09-15': 180,
      '2025-09-17': 300,
    }
    expect(recentAverage(log, goal, wednesday)).toBe(90) // (120 + 60 + 180 + 0) / 4
  })
})

describe('planDay', () => {
  it('splits weekday time between module lessons and DSA', () => {
    expect(planDay(300, wednesday)).toEqual([
      { stream: 'module', minutes: 195 },
      { stream: 'dsa', minutes: 105 },
    ])
  })

  it('merges blocks too small to be useful', () => {
    expect(planDay(45, wednesday)).toEqual([{ stream: 'module', minutes: 45 }])
  })

  it('uses Saturday for architecture and the project', () => {
    expect(planDay(180, new Date(2025, 8, 20)).map((b) => b.stream)).toEqual([
      'architecture',
      'project',
    ])
  })

  it('always adds up to the available time (rounded to 5 minutes)', () => {
    for (const minutes of [30, 70, 125, 241, 300]) {
      const total = planDay(minutes, wednesday).reduce((sum, b) => sum + b.minutes, 0)
      expect(total).toBe(Math.round(minutes / 5) * 5)
    }
  })

  it('plans nothing for zero minutes', () => {
    expect(planDay(0, wednesday)).toEqual([])
  })
})

describe('weeklyBudget', () => {
  it('adds up the study days at the target pace', () => {
    expect(weeklyBudget(goal, wednesday)).toEqual({
      module: 975,
      dsa: 525,
      architecture: 150,
      project: 150,
    })
  })
})

describe('timer and log helpers', () => {
  it('measures whole minutes and caps forgotten timers', () => {
    expect(elapsedMinutes('2025-09-17T10:00:00.000Z', new Date('2025-09-17T10:42:59.000Z'))).toBe(
      42,
    )
    expect(elapsedMinutes('2025-09-17T00:00:00.000Z', new Date('2025-09-18T00:00:00.000Z'))).toBe(
      480,
    )
    expect(elapsedMinutes('not a date', wednesday)).toBe(0)
  })

  it('adds and removes minutes without going negative', () => {
    const log = addMinutes({}, '2025-09-17', 30)
    expect(log).toEqual({ '2025-09-17': 30 })
    expect(addMinutes(log, '2025-09-17', -45)).toEqual({})
  })
})

describe('pace and finish estimates', () => {
  it('uses the recent pace only with enough history', () => {
    const few = { '2025-09-15': 120, '2025-09-16': 120 }
    expect(weeklyPace(few, goal, wednesday)).toEqual({ target: 1800, recent: null })
    const log = Object.fromEntries(
      Array.from({ length: 10 }, (_, i) => [dateKey(new Date(2025, 8, 7 + i)), 120]),
    )
    // Sep 7–16: 8 study days × 120 min (Sep 7 and 14 are Sundays = rest days)
    expect(weeklyPace(log, goal, wednesday)).toEqual({ target: 1800, recent: 720 })
  })

  it('turns hours into months and dates', () => {
    const eta = estimateFinish(130, 260, 1800, wednesday)! // 30 h/week
    expect(eta.monthsMin).toBeCloseTo(1, 1)
    expect(eta.monthsMax).toBeCloseTo(2, 1)
    expect(dateKey(eta.from)).toBe('2025-10-18') // 130 h / 30 h = 4.33 weeks → 31 days
    expect(estimateFinish(10, 20, 0, wednesday)).toBeNull()
  })
})

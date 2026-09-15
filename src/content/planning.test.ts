import { describe, expect, it } from 'vitest'
import type { LessonMeta } from '../types/content'
import { matchesPrefix, milestonesRemaining, orderedStream, pickForBudget } from './planning'

const core = { be: 'core', fe: 'core', fs: 'core', ai: 'core', ops: 'core' } as const
const lesson = (id: string, durationMinutes = 60, roles: LessonMeta['roles'] = core) =>
  ({ id, durationMinutes, roles }) as LessonMeta

describe('matchesPrefix', () => {
  it('matches whole path segments only', () => {
    expect(matchesPrefix('modules/m1/w0/01-a', 'modules/m1')).toBe(true)
    expect(matchesPrefix('modules/m10/w0/01-a', 'modules/m1')).toBe(false)
  })

  it('matches numbered project pages', () => {
    expect(matchesPrefix('projects/careerpilot/01-phase-1', 'projects/careerpilot/01')).toBe(true)
    expect(matchesPrefix('projects/careerpilot/02-phase-2', 'projects/careerpilot/01')).toBe(false)
  })
})

describe('planning', () => {
  const lessons = [lesson('modules/m2/w1/01-x'), lesson('modules/m1/w0/01-a'), lesson('modules/m1/w0/02-b')]

  it('orders lessons by the study path', () => {
    const ids = orderedStream(['modules/m1', 'modules/m2'], lessons).map((l) => l.id)
    expect(ids).toEqual(['modules/m1/w0/01-a', 'modules/m1/w0/02-b', 'modules/m2/w1/01-x'])
  })

  it('picks unfinished lessons until the budget is used', () => {
    const stream = orderedStream(['modules/m1', 'modules/m2'], lessons)
    const picked = pickForBudget(stream, { 'modules/m1/w0/01-a': 'done' }, 'fs', 120)
    expect(picked.map((l) => l.id)).toEqual(['modules/m1/w0/02-b', 'modules/m2/w1/01-x'])
  })

  it('always picks at least one lesson and skips optional ones', () => {
    const optional = { ...core, fs: 'optional' } as const
    const stream = [lesson('a', 30, optional), lesson('b', 500)]
    expect(pickForBudget(stream, {}, 'fs', 60).map((l) => l.id)).toEqual(['b'])
  })
})

describe('milestonesRemaining', () => {
  const milestones = [
    { id: 'one', include: ['modules/m1'], hours: { min: 10, max: 20 } },
    { id: 'two', include: ['modules/m1', 'modules/m2'], hours: { min: 5, max: 5 } },
  ] as never
  const lessons = [lesson('modules/m1/w0/01-a', 120), lesson('modules/m1/w0/02-b', 180), lesson('modules/m2/w1/01-x', 60)]

  it('subtracts finished lessons and adds earlier milestones', () => {
    const result = milestonesRemaining(milestones, lessons, { 'modules/m1/w0/01-a': 'x', 'modules/m2/w1/01-x': 'x' })
    expect(result).toEqual([
      { id: 'one', doneHours: 2, remainingMin: 8, remainingMax: 18 },
      // m1 lessons were already counted in milestone one; only the m2 hour counts here
      { id: 'two', doneHours: 1, remainingMin: 12, remainingMax: 22 },
    ])
  })

  it('never goes below zero for a milestone', () => {
    const many = Object.fromEntries(lessons.map((l) => [l.id, 'x']))
    const big = [{ id: 'one', include: ['modules'], hours: { min: 1, max: 2 } }] as never
    expect(milestonesRemaining(big, lessons, many)[0]).toMatchObject({ remainingMin: 0, remainingMax: 0 })
  })
})

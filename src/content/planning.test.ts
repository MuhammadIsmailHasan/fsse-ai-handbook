import { describe, expect, it } from 'vitest'
import type { LessonMeta } from '../types/content'
import { matchesPrefix, orderedStream, pickForBudget } from './planning'

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

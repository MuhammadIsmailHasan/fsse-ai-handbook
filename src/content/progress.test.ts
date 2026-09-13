import { describe, expect, it } from 'vitest'
import type { LessonMeta } from '../types/content'
import { countCoreProgress, countProgress, isVisibleForRole } from './progress'

function lesson(id: string, roles: Partial<LessonMeta['roles']> = {}): LessonMeta {
  return {
    id,
    roles: { be: 'core', fe: 'none', fs: 'core', ai: 'optional', ops: 'none', ...roles },
  } as LessonMeta
}

describe('progress', () => {
  const lessons = [lesson('a'), lesson('b', { fs: 'optional' }), lesson('c')]
  const completed = { a: '2026-09-13T00:00:00Z' }

  it('counts done lessons and percent', () => {
    expect(countProgress(lessons, completed)).toEqual({ done: 1, total: 3, percent: 33 })
  })

  it('handles empty lists without dividing by zero', () => {
    expect(countProgress([], completed).percent).toBe(0)
  })

  it('counts only core lessons for a role', () => {
    expect(countCoreProgress(lessons, completed, 'fs')).toEqual({ done: 1, total: 2, percent: 50 })
  })

  it('hides not-needed lessons only when asked', () => {
    expect(isVisibleForRole(lessons[0]!, 'fe', false)).toBe(true)
    expect(isVisibleForRole(lessons[0]!, 'fe', true)).toBe(false)
  })
})

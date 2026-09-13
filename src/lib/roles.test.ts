import { describe, expect, it } from 'vitest'
import { isTargetRole, levelFor, maxLevel } from './roles'

const roles = {
  be: 'core',
  fe: 'none',
  fs: 'optional',
  ai: 'recommended',
  ops: 'optional',
} as const

describe('roles', () => {
  it('picks the more important level', () => {
    expect(maxLevel('optional', 'core')).toBe('core')
    expect(maxLevel('none', 'optional')).toBe('optional')
  })

  it('returns the level for a single role', () => {
    expect(levelFor(roles, 'be')).toBe('core')
    expect(levelFor(roles, 'fe')).toBe('none')
  })

  it('combines FS and AI for the AI Full-Stack preset', () => {
    expect(levelFor(roles, 'ai-fs')).toBe('recommended')
  })

  it('validates target role values from storage', () => {
    expect(isTargetRole('ai-fs')).toBe(true)
    expect(isTargetRole('designer')).toBe(false)
  })
})

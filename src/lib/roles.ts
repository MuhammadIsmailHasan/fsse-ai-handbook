/**
 * roles.ts — logic for "how important is this lesson for MY target role?"
 *
 * Teaches: keeping business rules in plain functions (easy to test), separate from UI.
 */
import type { Level, RoleCode, RoleLabels } from '../types/content'

/** A single role, or the ⭐ AI Full-Stack preset (FS + AI combined). */
export type TargetRole = RoleCode | 'ai-fs'

export const TARGET_ROLES: { id: TargetRole; label: string; description: string }[] = [
  { id: 'ai-fs', label: '⭐ AI Full-Stack', description: 'Full-Stack + AI Engineer combined' },
  { id: 'fs', label: '🟪 Full-Stack Developer', description: 'Backend + frontend' },
  { id: 'ai', label: '🤖 AI Engineer', description: 'Building products with LLMs' },
  { id: 'be', label: '🟦 Backend Developer', description: 'APIs, databases, services' },
  { id: 'fe', label: '🟩 Frontend Developer', description: 'UI, React, Next.js' },
  { id: 'ops', label: '☁️ Cloud / DevOps Engineer', description: 'CI/CD, cloud, infrastructure' },
]

const RANK: Record<Level, number> = { none: 0, optional: 1, recommended: 2, core: 3 }

/** The more important of two levels. */
export function maxLevel(a: Level, b: Level): Level {
  return RANK[a] >= RANK[b] ? a : b
}

export function levelFor(roles: RoleLabels, target: TargetRole): Level {
  return target === 'ai-fs' ? maxLevel(roles.fs, roles.ai) : roles[target]
}

export function isTargetRole(value: unknown): value is TargetRole {
  return TARGET_ROLES.some((role) => role.id === value)
}

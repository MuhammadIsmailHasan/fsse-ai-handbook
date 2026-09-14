/**
 * roles.ts — logic for "how important is this lesson for MY target role?"
 *
 * Teaches: keeping business rules in plain functions (easy to test), separate from UI.
 */
import type { MessageKey } from '../i18n/messages'
import type { Level, RoleCode, RoleLabels } from '../types/content'

/** A single role, or the ⭐ AI Full-Stack preset (FS + AI combined). */
export type TargetRole = RoleCode | 'ai-fs'

/** Job titles stay in English in both languages (that's how job ads write them). */
export const TARGET_ROLES: { id: TargetRole; label: string; descriptionKey: MessageKey }[] = [
  { id: 'ai-fs', label: '⭐ AI Full-Stack', descriptionKey: 'role.aiFs.description' },
  { id: 'fs', label: '🟪 Full-Stack Developer', descriptionKey: 'role.fs.description' },
  { id: 'ai', label: '🤖 AI Engineer', descriptionKey: 'role.ai.description' },
  { id: 'be', label: '🟦 Backend Developer', descriptionKey: 'role.be.description' },
  { id: 'fe', label: '🟩 Frontend Developer', descriptionKey: 'role.fe.description' },
  { id: 'ops', label: '☁️ Cloud / DevOps Engineer', descriptionKey: 'role.ops.description' },
]

export function targetRoleLabel(id: TargetRole): string {
  return TARGET_ROLES.find((role) => role.id === id)?.label ?? id
}

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

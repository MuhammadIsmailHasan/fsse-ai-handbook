/**
 * roles.ts — display names, icons and colors for job roles and importance levels.
 *
 * Teaches: `Record<Union, Value>` forces an entry for EVERY role/level —
 * add a new role to the schema and TypeScript tells you to add it here too.
 */
import type { MessageKey } from '../i18n/messages'
import type { Level, RoleCode } from '../types/content'

export const ROLE_INFO: Record<RoleCode, { short: string; name: string; icon: string }> = {
  be: { short: 'BE', name: 'Backend Developer', icon: '🟦' },
  fe: { short: 'FE', name: 'Frontend Developer', icon: '🟩' },
  fs: { short: 'FS', name: 'Full-Stack Developer', icon: '🟪' },
  ai: { short: 'AI', name: 'AI Engineer', icon: '🤖' },
  ops: { short: 'Ops', name: 'Cloud / DevOps Engineer', icon: '☁️' },
}

export const LEVEL_INFO: Record<Level, { labelKey: MessageKey; icon: string; className: string }> =
  {
    core: {
      labelKey: 'level.core',
      icon: '🟢',
      className:
        'bg-emerald-50 text-emerald-700 ring-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-300 dark:ring-emerald-500/30',
    },
    recommended: {
      labelKey: 'level.recommended',
      icon: '🔵',
      className:
        'bg-sky-50 text-sky-700 ring-sky-200 dark:bg-sky-500/10 dark:text-sky-300 dark:ring-sky-500/30',
    },
    optional: {
      labelKey: 'level.optional',
      icon: '⚪',
      className:
        'bg-slate-50 text-slate-600 ring-slate-200 dark:bg-slate-800/60 dark:text-slate-300 dark:ring-slate-700',
    },
    none: {
      labelKey: 'level.none',
      icon: '➖',
      className:
        'bg-transparent text-slate-400 ring-slate-200 dark:text-slate-500 dark:ring-slate-800',
    },
  }

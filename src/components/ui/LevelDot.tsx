/**
 * LevelDot.tsx — a tiny colored dot showing a lesson's importance for the target role.
 */
import { LEVEL_INFO } from '../../config/roles'
import { useLocale } from '../../hooks/useLocale'
import type { Level } from '../../types/content'

const DOT: Record<Level, string> = {
  core: 'bg-emerald-500',
  recommended: 'bg-sky-500',
  optional: 'bg-slate-300 dark:bg-slate-600',
  none: 'border border-slate-300 dark:border-slate-600',
}

export function LevelDot({ level }: { level: Level }) {
  const { t } = useLocale()
  const label = t(LEVEL_INFO[level].labelKey)

  return (
    <span className={`inline-block h-2 w-2 shrink-0 rounded-full ${DOT[level]}`} title={label}>
      <span className="sr-only">{label}</span>
    </span>
  )
}

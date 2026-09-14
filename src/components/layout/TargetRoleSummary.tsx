/**
 * TargetRoleSummary.tsx — "🎯 My target role" card at the top of the sidebar.
 */
import { Link } from 'react-router'
import { countCoreProgress } from '../../content/progress'
import { useContent } from '../../hooks/useContent'
import { useLocale } from '../../hooks/useLocale'
import { useStudy } from '../../hooks/useStudy'
import { targetRoleLabel } from '../../lib/roles'
import { ProgressBar } from '../ui/ProgressBar'

export function TargetRoleSummary({ onNavigate }: { onNavigate: () => void }) {
  const { targetRole, completed } = useStudy()
  const { allLessons } = useContent()
  const { t } = useLocale()
  const core = countCoreProgress(allLessons, completed, targetRole)

  return (
    <Link
      to="/settings"
      onClick={onNavigate}
      className="block rounded-xl border border-slate-200 p-3 hover:border-indigo-300 dark:border-slate-800 dark:hover:border-indigo-500/50"
    >
      <p className="text-[0.7rem] font-semibold tracking-wider text-slate-400 uppercase">
        {t('targetRole.heading')}
      </p>
      <p className="mt-0.5 text-sm font-medium text-slate-900 dark:text-white">
        {targetRoleLabel(targetRole)}
      </p>
      <div className="mt-2 flex items-center gap-2">
        <ProgressBar percent={core.percent} label={t('targetRole.coreDone')} />
        <span className="shrink-0 text-xs text-slate-500 tabular-nums">
          {t('targetRole.core', { done: core.done, total: core.total })}
        </span>
      </div>
    </Link>
  )
}

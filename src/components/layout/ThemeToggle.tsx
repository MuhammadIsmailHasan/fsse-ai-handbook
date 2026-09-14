/**
 * ThemeToggle.tsx — cycles Light → Dark → System.
 *
 * Teaches: consuming context through a custom hook (`useTheme`), and
 * looking up "what comes next" with a plain object instead of if/else chains.
 */
import { useLocale } from '../../hooks/useLocale'
import { useTheme, type ThemePreference } from '../../hooks/useTheme'
import { Icon, type IconName } from '../ui/Icon'

const NEXT: Record<ThemePreference, ThemePreference> = {
  light: 'dark',
  dark: 'system',
  system: 'light',
}

const ICON: Record<ThemePreference, IconName> = {
  light: 'sun',
  dark: 'moon',
  system: 'monitor',
}

export function ThemeToggle() {
  const { preference, setPreference } = useTheme()
  const { t } = useLocale()
  const current = t(`theme.${preference}`)
  const next = t(`theme.${NEXT[preference]}`)

  return (
    <button
      type="button"
      onClick={() => setPreference(NEXT[preference])}
      className="rounded-md p-2 text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
      aria-label={t('theme.toggle', { current, next })}
      title={t('theme.title', { current })}
    >
      <Icon name={ICON[preference]} />
    </button>
  )
}

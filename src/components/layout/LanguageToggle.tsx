/**
 * LanguageToggle.tsx — switches between English and Bahasa Indonesia.
 *
 * Shows the CURRENT language ("EN" / "ID"); clicking moves to the other one.
 * The aria-label says both, so screen reader users know what will happen.
 */
import { useLocale } from '../../hooks/useLocale'
import { LOCALE_INFO, type Locale } from '../../i18n/messages'

const NEXT: Record<Locale, Locale> = { en: 'id', id: 'en' }

export function LanguageToggle() {
  const { locale, setLocale, t } = useLocale()
  const next = NEXT[locale]

  return (
    <button
      type="button"
      onClick={() => setLocale(next)}
      className="rounded-md px-2 py-1.5 text-xs font-semibold tracking-wide text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
      aria-label={t('language.toggle', {
        current: LOCALE_INFO[locale].name,
        next: LOCALE_INFO[next].name,
      })}
      title={t('language.title')}
    >
      <span aria-hidden="true">{LOCALE_INFO[locale].flag}</span> {LOCALE_INFO[locale].short}
    </button>
  )
}

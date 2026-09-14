/**
 * useLocale.ts — read and change the app language from any component.
 *
 * Same pattern as useTheme: a Context holds the value, a custom hook reads it
 * and fails fast if the provider is missing.
 *
 *   const { t, locale } = useLocale()
 *   t('lesson.readMinutes', { minutes: 12 })  // "📖 12 min read" / "📖 12 menit baca"
 */
import { createContext, useContext } from 'react'
import type { Locale, MessageKey, MessageValues } from '../i18n/messages'

export type LocaleContextValue = {
  locale: Locale
  setLocale: (locale: Locale) => void
  /** Translate a UI message key, filling in {placeholders}. */
  t: (key: MessageKey, values?: MessageValues) => string
  /** Format a number the local way: 1.5 (en) vs 1,5 (id). */
  formatNumber: (value: number) => string
}

export const LocaleContext = createContext<LocaleContextValue | null>(null)

export function useLocale(): LocaleContextValue {
  const context = useContext(LocaleContext)
  if (!context) {
    throw new Error('useLocale() must be used inside <LocaleProvider>.')
  }
  return context
}

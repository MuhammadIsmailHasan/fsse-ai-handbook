/**
 * LocaleProvider.tsx — owns the language choice (English / Bahasa Indonesia).
 *
 * Teaches:
 * - Detecting a sensible default from the browser (`navigator.languages`),
 *   but letting a saved choice win.
 * - Keeping `<html lang>` in sync, so screen readers pronounce text correctly
 *   and the browser's spellcheck/hyphenation use the right language.
 */
import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { LocaleContext } from '../hooks/useLocale'
import {
  isLocale,
  translate,
  type Locale,
  type MessageKey,
  type MessageValues,
} from '../i18n/messages'
import { readJSON, STORAGE_KEYS, writeJSON } from '../lib/storage'

function detectLocale(): Locale {
  const saved = readJSON<unknown>(STORAGE_KEYS.locale, null)
  if (isLocale(saved)) return saved
  // Only the browser's FIRST language counts — English stays the default otherwise.
  const primary = typeof navigator === 'undefined' ? '' : navigator.language
  return primary.toLowerCase().startsWith('id') ? 'id' : 'en'
}

export function LocaleProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(detectLocale)

  useEffect(() => {
    document.documentElement.lang = locale
  }, [locale])

  const setLocale = useCallback((next: Locale) => {
    setLocaleState(next)
    writeJSON(STORAGE_KEYS.locale, next)
  }, [])

  const value = useMemo(() => {
    const intlLocale = locale === 'id' ? 'id-ID' : 'en-US'
    const numberFormat = new Intl.NumberFormat(intlLocale)
    return {
      locale,
      setLocale,
      intlLocale,
      t: (key: MessageKey, values?: MessageValues) => translate(locale, key, values),
      formatNumber: (n: number) => numberFormat.format(n),
      formatDuration: (minutes: number) => {
        const h = Math.floor(Math.max(0, minutes) / 60)
        const m = Math.round(Math.max(0, minutes) % 60)
        if (h === 0) return translate(locale, 'time.minutes', { m })
        if (m === 0) return translate(locale, 'time.hours', { h })
        return translate(locale, 'time.hoursMinutes', { h, m })
      },
    }
  }, [locale, setLocale])

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>
}

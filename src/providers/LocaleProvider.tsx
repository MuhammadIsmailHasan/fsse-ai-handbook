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
    const numberFormat = new Intl.NumberFormat(locale === 'id' ? 'id-ID' : 'en-US')
    return {
      locale,
      setLocale,
      t: (key: MessageKey, values?: MessageValues) => translate(locale, key, values),
      formatNumber: (n: number) => numberFormat.format(n),
    }
  }, [locale, setLocale])

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>
}

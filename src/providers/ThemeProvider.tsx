/**
 * ThemeProvider.tsx — owns the theme state and applies it to <html>.
 *
 * Teaches:
 * - `useState` with a lazy initializer: read localStorage only once, on first render.
 * - `useSyncExternalStore`: the React-approved way to subscribe to something
 *   OUTSIDE React (here: the OS dark-mode setting).
 * - `useEffect` for side effects: touching the DOM after render.
 * - `useMemo` / `useCallback`: keep the context value stable so consumers
 *   don't re-render for no reason.
 */
import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  useSyncExternalStore,
  type ReactNode,
} from 'react'
import { ThemeContext, type ResolvedTheme, type ThemePreference } from '../hooks/useTheme'
import { readJSON, STORAGE_KEYS, writeJSON } from '../lib/storage'

const DARK_QUERY = '(prefers-color-scheme: dark)'

function subscribeToSystemTheme(onChange: () => void) {
  const media = window.matchMedia(DARK_QUERY)
  media.addEventListener('change', onChange)
  // Return a cleanup function — React calls it when unsubscribing.
  return () => media.removeEventListener('change', onChange)
}

function getSystemPrefersDark() {
  return window.matchMedia(DARK_QUERY).matches
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [preference, setPreferenceState] = useState<ThemePreference>(() =>
    readJSON<ThemePreference>(STORAGE_KEYS.theme, 'system'),
  )
  const systemPrefersDark = useSyncExternalStore(subscribeToSystemTheme, getSystemPrefersDark)

  // Derived value: computed during render, not stored in state.
  // (Storing it in state would risk the two getting out of sync.)
  const resolved: ResolvedTheme =
    preference === 'system' ? (systemPrefersDark ? 'dark' : 'light') : preference

  useEffect(() => {
    const root = document.documentElement
    root.classList.toggle('dark', resolved === 'dark')
    root.style.colorScheme = resolved
  }, [resolved])

  const setPreference = useCallback((next: ThemePreference) => {
    setPreferenceState(next)
    writeJSON(STORAGE_KEYS.theme, next)
  }, [])

  const value = useMemo(
    () => ({ preference, resolved, setPreference }),
    [preference, resolved, setPreference],
  )

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

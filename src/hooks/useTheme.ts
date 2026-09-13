/**
 * useTheme.ts — read and change the color theme from any component.
 *
 * Teaches:
 * - React Context: share a value with the whole tree without passing props down
 *   through every level ("prop drilling").
 * - Custom hooks: `useTheme()` hides the context details behind a friendly API.
 * - Failing fast: throwing a clear error if the provider is missing.
 */
import { createContext, useContext } from 'react'

export type ThemePreference = 'light' | 'dark' | 'system'
export type ResolvedTheme = 'light' | 'dark'

export type ThemeContextValue = {
  /** What the user chose. */
  preference: ThemePreference
  /** What is actually shown (system → light or dark). */
  resolved: ResolvedTheme
  setPreference: (preference: ThemePreference) => void
}

// `null` default means "no provider above me" — useTheme() checks for it.
export const ThemeContext = createContext<ThemeContextValue | null>(null)

export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme() must be used inside <ThemeProvider>.')
  }
  return context
}

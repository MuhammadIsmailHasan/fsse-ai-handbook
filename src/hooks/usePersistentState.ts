/**
 * usePersistentState.ts — like useState, but remembered in localStorage.
 *
 * Teaches:
 * - Writing your own generic hook: `usePersistentState<number>('key', 0)`.
 * - What effects are FOR: keeping React state in sync with an external system
 *   (here, localStorage) after each change.
 */
import { useEffect, useState } from 'react'
import { readJSON, writeJSON } from '../lib/storage'

export function usePersistentState<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => readJSON(key, initialValue))

  useEffect(() => {
    writeJSON(key, value)
  }, [key, value])

  // `as const` keeps the tuple type [T, setter] instead of (T | setter)[]
  return [value, setValue] as const
}

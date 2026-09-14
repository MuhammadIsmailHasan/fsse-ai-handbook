/**
 * storage.ts — tiny, safe wrappers around the browser's localStorage.
 *
 * Teaches:
 * - Generics: `readJSON<T>` returns whatever type you ask for.
 * - Defensive code: localStorage can throw (private mode, full storage, bad JSON),
 *   so every access is wrapped in try/catch and falls back gracefully.
 *
 * All progress lives in the browser. Settings → "Export progress" (built later)
 * lets you back it up as a JSON file.
 */

/** Every key we store, in one place, so names never drift apart. */
export const STORAGE_KEYS = {
  theme: 'fsse:theme',
  locale: 'fsse:locale',
  progress: 'fsse:progress',
  targetRole: 'fsse:target-role',
  notes: 'fsse:notes',
  reviewQueue: 'fsse:review-queue',
  placement: 'fsse:placement',
  preferences: 'fsse:preferences',
} as const

export function readJSON<T>(key: string, fallback: T): T {
  try {
    const raw = window.localStorage.getItem(key)
    return raw === null ? fallback : (JSON.parse(raw) as T)
  } catch {
    return fallback
  }
}

export function writeJSON<T>(key: string, value: T): void {
  try {
    window.localStorage.setItem(key, JSON.stringify(value))
  } catch {
    // Storage unavailable — the app still works, it just won't remember this.
  }
}

export function removeKey(key: string): void {
  try {
    window.localStorage.removeItem(key)
  } catch {
    // ignore
  }
}

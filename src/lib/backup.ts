/**
 * backup.ts — export and import everything the app stores in this browser.
 *
 * Teaches:
 * - Blobs + object URLs: create a file in memory and let the browser download it.
 * - Validating untrusted input (an uploaded file) before using it.
 */
import { STORAGE_KEYS } from './storage'

const KNOWN_KEYS = new Set<string>(Object.values(STORAGE_KEYS))

type Backup = {
  app: 'fsse-handbook'
  version: 1
  exportedAt: string
  data: Record<string, unknown>
}

export function createBackup(): Backup {
  const data: Record<string, unknown> = {}
  for (const key of KNOWN_KEYS) {
    const raw = window.localStorage.getItem(key)
    if (raw !== null) data[key] = JSON.parse(raw)
  }
  return { app: 'fsse-handbook', version: 1, exportedAt: new Date().toISOString(), data }
}

export function downloadBackup() {
  const backup = createBackup()
  const blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `fsse-handbook-progress-${backup.exportedAt.slice(0, 10)}.json`
  link.click()
  URL.revokeObjectURL(url) // free the memory
}

/** Returns the number of restored keys, or throws a friendly error. */
export async function restoreBackup(file: File): Promise<number> {
  let parsed: unknown
  try {
    parsed = JSON.parse(await file.text())
  } catch {
    throw new Error('This file is not valid JSON.')
  }

  const backup = parsed as Partial<Backup>
  if (backup?.app !== 'fsse-handbook' || typeof backup.data !== 'object' || backup.data === null) {
    throw new Error('This does not look like an FSSE Handbook backup file.')
  }

  let restored = 0
  for (const [key, value] of Object.entries(backup.data)) {
    if (!KNOWN_KEYS.has(key)) continue // ignore anything unexpected
    window.localStorage.setItem(key, JSON.stringify(value))
    restored++
  }
  return restored
}

export function clearAllData() {
  for (const key of KNOWN_KEYS) window.localStorage.removeItem(key)
}

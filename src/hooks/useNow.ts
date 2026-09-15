/**
 * useNow.ts — the current time, refreshed every `intervalMs`.
 *
 * Teaches: a timer is an external "system" — start it in an effect, and stop it
 * in the cleanup so it doesn't keep running after the component is gone.
 */
import { useEffect, useState } from 'react'

export function useNow(intervalMs = 1000, enabled = true): Date {
  const [now, setNow] = useState(() => new Date())

  useEffect(() => {
    if (!enabled) return
    const id = window.setInterval(() => setNow(new Date()), intervalMs)
    return () => window.clearInterval(id)
  }, [intervalMs, enabled])

  return now
}

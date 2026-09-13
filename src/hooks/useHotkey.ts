/**
 * useHotkey.ts — run a function when a keyboard shortcut is pressed.
 *
 * Teaches:
 * - Adding and REMOVING global event listeners in an effect (cleanup prevents leaks).
 * - Keeping the latest callback in a ref so the listener doesn't need re-attaching.
 */
import { useEffect, useRef } from 'react'

/** `key` is a letter like "k". Cmd (Mac) or Ctrl (Windows/Linux) must be held. */
export function useModHotkey(key: string, callback: () => void) {
  const callbackRef = useRef(callback)

  useEffect(() => {
    callbackRef.current = callback
  })

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === key) {
        event.preventDefault()
        callbackRef.current()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [key])
}

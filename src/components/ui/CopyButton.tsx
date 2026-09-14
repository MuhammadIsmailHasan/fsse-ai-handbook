/**
 * CopyButton.tsx — copies text to the clipboard and briefly shows "Copied".
 *
 * Teaches: browser APIs that return Promises (`navigator.clipboard`), and
 * cleaning up timers so they don't fire after the component is gone.
 */
import { useEffect, useRef, useState } from 'react'
import { useLocale } from '../../hooks/useLocale'

type CopyButtonProps = {
  /** Text to copy, or a function that returns it at click time. */
  text: string | (() => string)
  label?: string
  className?: string
}

export function CopyButton({ text, label, className }: CopyButtonProps) {
  const { t } = useLocale()
  const [copied, setCopied] = useState(false)
  const timer = useRef<number | undefined>(undefined)

  useEffect(() => () => window.clearTimeout(timer.current), [])

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(typeof text === 'function' ? text() : text)
      setCopied(true)
      window.clearTimeout(timer.current)
      timer.current = window.setTimeout(() => setCopied(false), 1500)
    } catch {
      // Clipboard can be blocked; nothing else to do.
    }
  }

  return (
    <button
      type="button"
      onClick={handleCopy}
      className={
        className ??
        'rounded px-2 py-0.5 font-sans text-xs font-medium text-slate-500 hover:bg-slate-200 hover:text-slate-800 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-100'
      }
    >
      {copied ? t('code.copied') : (label ?? t('code.copy'))}
    </button>
  )
}

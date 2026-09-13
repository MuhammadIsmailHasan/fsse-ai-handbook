/**
 * Mermaid.tsx — renders ```mermaid code blocks as diagrams.
 *
 * Teaches:
 * - Dynamic `import()`: Mermaid is large, so it's downloaded only when a page
 *   actually contains a diagram (code splitting).
 * - `useId()`: a unique, stable id per component instance.
 * - Re-rendering when the theme changes, so diagrams match light/dark mode.
 */
import { useEffect, useId, useState } from 'react'
import { useTheme } from '../../hooks/useTheme'

export function Mermaid({ code }: { code: string }) {
  const { resolved } = useTheme()
  const reactId = useId()
  const [state, setState] = useState<{ key: string; svg?: string; error?: string } | null>(null)
  const key = `${resolved}:${code}`

  useEffect(() => {
    let cancelled = false
    const elementId = `mermaid-${reactId.replace(/[^a-zA-Z0-9]/g, '')}`

    import('mermaid')
      .then(async ({ default: mermaid }) => {
        mermaid.initialize({
          startOnLoad: false,
          theme: resolved === 'dark' ? 'dark' : 'default',
          fontFamily: 'inherit',
        })
        const { svg } = await mermaid.render(elementId, code)
        if (!cancelled) setState({ key, svg })
      })
      .catch((error: unknown) => {
        if (!cancelled)
          setState({ key, error: error instanceof Error ? error.message : String(error) })
      })

    return () => {
      cancelled = true
    }
  }, [code, key, reactId, resolved])

  const current = state?.key === key ? state : null

  return (
    <figure className="not-prose my-6 overflow-x-auto rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
      {current?.svg && (
        <div className="flex justify-center" dangerouslySetInnerHTML={{ __html: current.svg }} />
      )}
      {current?.error && (
        <pre className="text-sm whitespace-pre-wrap text-red-600 dark:text-red-400">
          Diagram error: {current.error}
        </pre>
      )}
      {!current && <p className="text-sm text-slate-400">Drawing diagram…</p>}
    </figure>
  )
}

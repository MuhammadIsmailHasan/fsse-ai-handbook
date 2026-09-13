/**
 * CodeBlock.tsx — a highlighted code block with a language label and copy button.
 *
 * Teaches:
 * - Async work in effects: start the highlight, then update state when it finishes.
 * - Cancellation: if the code changes (or the component unmounts) before
 *   highlighting finishes, ignore the stale result.
 * - Progressive enhancement: plain <pre> first, pretty colors when ready.
 */
import { useEffect, useState } from 'react'
import { highlightCode } from '../../lib/highlighter'
import { CopyButton } from '../ui/CopyButton'

type CodeBlockProps = {
  code: string
  language: string
}

export function CodeBlock({ code, language }: CodeBlockProps) {
  const [result, setResult] = useState<{ source: string; html: string } | null>(null)

  useEffect(() => {
    let cancelled = false
    highlightCode(code, language)
      .then((html) => {
        if (!cancelled) setResult({ source: code, html })
      })
      .catch(() => {
        // Highlighting is a nice-to-have; the plain version stays visible.
      })
    return () => {
      cancelled = true
    }
  }, [code, language])

  // Only use the highlighted HTML if it belongs to the CURRENT code.
  const html = result?.source === code ? result.html : null

  return (
    <div className="not-prose group relative my-5 overflow-hidden rounded-xl border border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-1.5 text-xs text-slate-500 dark:border-slate-800 dark:text-slate-400">
        <span className="font-mono">{language === 'text' ? 'text' : language}</span>
        <CopyButton text={code} />
      </div>
      {html ? (
        // Shiki escapes the code itself, and the content is our own files.
        <div dangerouslySetInnerHTML={{ __html: html }} />
      ) : (
        <pre className="overflow-x-auto p-4 font-mono text-[0.85rem] leading-relaxed">
          <code>{code}</code>
        </pre>
      )}
    </div>
  )
}

/**
 * LinkedInCard.tsx — a post template to share progress, with a copy button.
 *
 * Markdown:
 *   :::linkedin{type="weekly"}
 *   Template text with [placeholders]…
 *   :::
 *
 * Teaches: `useRef` to read the rendered text of children at click time
 * (`innerText`), instead of duplicating the template as a string prop.
 */
import { useRef, type ReactNode } from 'react'
import { LINKEDIN_POSTS, LINKEDIN_RULES, type LinkedInPostType } from '../../config/linkedin'
import { CopyButton } from '../ui/CopyButton'

function isPostType(value: string | undefined): value is LinkedInPostType {
  return value !== undefined && value in LINKEDIN_POSTS
}

export function LinkedInCard({ type, children }: { type?: string; children?: ReactNode }) {
  const templateRef = useRef<HTMLDivElement>(null)
  const post = LINKEDIN_POSTS[isPostType(type) ? type : 'weekly']

  return (
    <section className="my-8 overflow-hidden rounded-xl border border-sky-200 dark:border-sky-500/30">
      <header className="not-prose flex items-center justify-between gap-2 bg-sky-50 px-5 py-3 dark:bg-sky-500/10">
        <p className="font-semibold text-slate-900 dark:text-white">
          Share your progress · {post.label}
        </p>
        <CopyButton
          text={() => templateRef.current?.innerText.trim() ?? ''}
          label="Copy template"
          className="rounded-md bg-sky-600 px-3 py-1 text-xs font-medium text-white hover:bg-sky-700"
        />
      </header>

      <div className="px-5 py-3">
        <div
          ref={templateRef}
          className="rounded-lg border border-dashed border-slate-300 bg-white px-4 dark:border-slate-700 dark:bg-slate-900"
        >
          {children}
        </div>

        <ul className="not-prose mt-3 space-y-1 text-xs text-slate-600 dark:text-slate-400">
          {[...post.tips, ...LINKEDIN_RULES].map((tip) => (
            <li key={tip}>• {tip}</li>
          ))}
        </ul>
      </div>
    </section>
  )
}

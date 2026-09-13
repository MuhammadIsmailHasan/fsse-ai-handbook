/**
 * ExerciseCard.tsx — a local (on your computer) exercise with automatic tests.
 *
 * Markdown:
 *   :::exercise{path="exercises/m1/w0/01-operators" ai="no-ai" title="Build a calculator"}
 *   What to do…
 *   :::
 *
 * Teaches: turning a data attribute (`ai`) into clear UI, and giving the user
 * the exact command to run — fewer "how do I start?" moments.
 */
import type { ReactNode } from 'react'
import { exerciseRunner } from '../../lib/exercise-commands'
import { CommandLine } from './CommandLine'

type ExerciseCardProps = {
  path?: string
  ai?: string
  title?: string
  children?: ReactNode
}

export function AiPolicyBadge({ ai }: { ai?: string }) {
  if (ai === 'ai-allowed') {
    return (
      <span
        className="rounded-full bg-sky-100 px-2 py-0.5 text-xs font-semibold text-sky-800 dark:bg-sky-500/15 dark:text-sky-300"
        title="Use AI if you like — but you must be able to explain every line."
      >
        🤖✅ AI-allowed
      </span>
    )
  }
  return (
    <span
      className="rounded-full bg-rose-100 px-2 py-0.5 text-xs font-semibold text-rose-800 dark:bg-rose-500/15 dark:text-rose-300"
      title="Brain-first: solve it yourself. Use AI only afterwards, to review."
    >
      🚫🤖 No-AI
    </span>
  )
}

export function ExerciseCard({ path, ai, title, children }: ExerciseCardProps) {
  const runner = path ? exerciseRunner(path) : undefined

  return (
    <section className="my-8 overflow-hidden rounded-xl border-2 border-indigo-200 dark:border-indigo-500/30">
      <header className="not-prose flex flex-wrap items-center justify-between gap-2 bg-indigo-50 px-5 py-3 dark:bg-indigo-500/10">
        <p className="font-semibold text-slate-900 dark:text-white">🧸 {title ?? 'Toy exercise'}</p>
        <AiPolicyBadge ai={ai} />
      </header>

      <div className="px-5 pt-1 pb-4">
        {children}

        {runner && (
          <div className="not-prose mt-4 space-y-2 text-sm">
            <p className="text-slate-600 dark:text-slate-400">
              📦 Folder: <code className="text-xs">{path}</code>
            </p>
            <p className="text-slate-600 dark:text-slate-400">
              🧪 Run the checks (from the project root):
            </p>
            <CommandLine command={runner.command} />
            {runner.kind === 'python' ? (
              <p className="text-xs text-slate-500">
                No uv? Use <code>python -m pytest {runner.relative}</code> inside{' '}
                <code>exercises/</code> — see <code>exercises/README.md</code>. Stuck? Try the hints
                first; open <code>solution/</code> only after a real attempt.
              </p>
            ) : (
              <p className="text-xs text-slate-500">
                First time? Run <code>npm install</code> inside <code>exercises/web</code>. Add{' '}
                <code>--watch</code> to re-run on every save. Open <code>solution/</code> only after
                a real attempt.
              </p>
            )}
          </div>
        )}
      </div>
    </section>
  )
}

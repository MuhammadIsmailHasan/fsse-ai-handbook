/**
 * AiReviewSlot.tsx — placeholder for FUTURE AI feedback on explain/design answers.
 *
 * Markdown:  ::ai-review{task="explain"}
 *
 * See src/lib/ai-review/types.ts for the planned interface.
 */
import { AI_REVIEW_ENABLED } from '../../lib/ai-review/types'

export function AiReviewSlot() {
  return (
    <div className="not-prose my-6 flex flex-wrap items-center gap-3 rounded-xl border border-dashed border-slate-300 px-4 py-3 dark:border-slate-700">
      <button
        type="button"
        disabled
        className="cursor-not-allowed rounded-lg bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-400 dark:bg-slate-800"
      >
        🤖 Ask AI to review
      </button>
      <p className="text-xs text-slate-500">
        {AI_REVIEW_ENABLED
          ? 'AI review is switched on in .env, but not built yet.'
          : 'Coming later (local Ollama first). For now, use the self-review checklist above — then compare with a friend or mentor.'}
      </p>
    </div>
  )
}

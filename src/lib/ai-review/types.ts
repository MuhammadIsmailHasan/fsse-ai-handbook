/**
 * ai-review/types.ts — the contract for FUTURE AI feedback (not implemented yet).
 *
 * Designing the interface now means adding a provider later (Ollama first, then
 * Gemini/Groq/OpenRouter) won't require changing the lesson components.
 *
 * Teaches: "program to an interface" — components depend on `ReviewProvider`,
 * not on any specific AI service.
 */

export type ReviewProviderId = 'ollama' | 'gemini' | 'openrouter' | 'groq'

export type ReviewRequest = {
  lessonId: string
  /** What the learner was asked to do, e.g. "Explain REST to a non-programmer". */
  task: string
  answer: string
  /** The self-review checklist items, used as the grading rubric. */
  rubric: string[]
}

export type ReviewResult = {
  summary: string
  strengths: string[]
  improvements: string[]
  /** One entry per rubric item. */
  rubricScores: { item: string; met: boolean; comment: string }[]
}

export interface ReviewProvider {
  id: ReviewProviderId
  review(request: ReviewRequest): Promise<ReviewResult>
}

export const AI_REVIEW_ENABLED = import.meta.env.VITE_AI_REVIEW_ENABLED === 'true'

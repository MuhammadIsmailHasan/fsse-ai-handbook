/**
 * linkedin.ts — post types and writing tips for "learning in public".
 */
export type LinkedInPostType = 'weekly' | 'concept' | 'dsa' | 'build' | 'reflection' | 'milestone'

export const LINKEDIN_POSTS: Record<LinkedInPostType, { label: string; tips: string[] }> = {
  weekly: {
    label: '📣 Weekly recap',
    tips: [
      'Hook: start with one surprising thing you learned — not "This week I learned…".',
      'Keep it to 3 bullet points and one small struggle you overcame.',
      'Add a visual: a diagram, a code snippet screenshot or your progress bar.',
    ],
  },
  concept: {
    label: '💡 Explained simply',
    tips: [
      'Reuse your Part 2 "Explain it" answer — it is already written for non-programmers.',
      'One concept per post. An analogy beats a definition.',
      'End with a question to invite comments.',
    ],
  },
  dsa: {
    label: '🧩 Pattern + problem',
    tips: [
      'Name the pattern, show how you recognized it, and share the time complexity.',
      'Never paste full solutions to problems from paid platforms — describe the approach.',
    ],
  },
  build: {
    label: '🚀 Build in public',
    tips: [
      'Show, don’t tell: a GIF or short video of the feature working.',
      'Share one technical decision and why you made it (the trade-off).',
      'Link the GitHub repo — make sure the README is ready first.',
    ],
  },
  reflection: {
    label: '🎓 Module reflection',
    tips: [
      'What you built, what was hardest, what you would do differently.',
      'Be specific: numbers (tests written, endpoints, pages) make it credible.',
    ],
  },
  milestone: {
    label: '🎯 Milestone / open to work',
    tips: [
      'Summarize skills with proof: link 1–2 projects, not a long list of tools.',
      'Say clearly what roles you are looking for and where (remote / city).',
    ],
  },
}

export const LINKEDIN_RULES = [
  'Rewrite the template in your own voice — recruiters notice copy-paste posts.',
  'Don’t share the bootcamp’s paid course material (slides, lesson text, assignment briefs).',
  'Suggested hashtags: pick 3–5, e.g. #LearningInPublic #FullStack #Python #React #AIEngineering',
]

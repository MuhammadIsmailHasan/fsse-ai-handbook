/**
 * search.ts — fuzzy search over lesson metadata with Fuse.js.
 *
 * Teaches:
 * - Fuzzy matching: "fastap" still finds "FastAPI".
 * - Weighted fields: a match in the title matters more than one in the excerpt.
 * - Building the index lazily, only when someone actually searches.
 */
import Fuse from 'fuse.js'
import { allLessons } from '../content'
import type { LessonMeta } from '../types/content'

let fuse: Fuse<LessonMeta> | null = null

function getIndex() {
  fuse ??= new Fuse(allLessons, {
    includeScore: true,
    ignoreLocation: true, // match anywhere in the text, not just near the start
    threshold: 0.35, // 0 = exact only, 1 = match anything
    keys: [
      { name: 'title', weight: 3 },
      { name: 'tags', weight: 2 },
      { name: 'headings', weight: 2 },
      { name: 'summary', weight: 1.5 },
      { name: 'excerpt', weight: 1 },
    ],
  })
  return fuse
}

export function searchLessons(query: string, limit = 12): LessonMeta[] {
  const trimmed = query.trim()
  if (trimmed.length < 2) return []
  return getIndex()
    .search(trimmed, { limit })
    .map((result) => result.item)
}

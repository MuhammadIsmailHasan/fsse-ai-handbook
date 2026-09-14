/**
 * search.ts — fuzzy search over lesson metadata with Fuse.js.
 *
 * Teaches:
 * - Fuzzy matching: "fastap" still finds "FastAPI".
 * - Weighted fields: a match in the title matters more than one in the excerpt.
 * - Building the index lazily, only when someone actually searches — and once per
 *   lesson list (one per language), cached in a WeakMap keyed by that array.
 */
import Fuse from 'fuse.js'
import type { LessonMeta } from '../types/content'

const indexes = new WeakMap<LessonMeta[], Fuse<LessonMeta>>()

function getIndex(lessons: LessonMeta[]) {
  let fuse = indexes.get(lessons)
  if (!fuse) {
    fuse = new Fuse(lessons, {
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
    indexes.set(lessons, fuse)
  }
  return fuse
}

export function searchLessons(query: string, lessons: LessonMeta[], limit = 12): LessonMeta[] {
  const trimmed = query.trim()
  if (trimmed.length < 2) return []
  return getIndex(lessons)
    .search(trimmed, { limit })
    .map((result) => result.item)
}

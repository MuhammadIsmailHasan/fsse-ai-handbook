/**
 * i18n-hash.ts — fingerprint of the English text a translation was made from.
 *
 * Only title, summary and body count (see translatableText), so bumping roles or
 * `lastReviewed` doesn't mark translations stale. Node-only (uses node:crypto),
 * so it lives in scripts/, not in the browser code.
 */
import { createHash } from 'node:crypto'
import { translatableText } from '../src/content/parse.ts'

export function sourceHash(englishSource: string): string {
  return createHash('sha256').update(translatableText(englishSource)).digest('hex').slice(0, 12)
}

/**
 * useContent.ts — course data in the language the learner picked.
 *
 *   const { course, getLesson, allLessons } = useContent()
 *
 * Teaches: composing hooks. `useContent` builds on `useLocale`, so components
 * never have to pass the locale around by hand.
 */
import { getContent, type ContentApi } from '../content'
import { useLocale } from './useLocale'

export function useContent(): ContentApi {
  const { locale } = useLocale()
  return getContent(locale)
}

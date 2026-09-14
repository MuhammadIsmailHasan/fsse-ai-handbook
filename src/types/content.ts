/**
 * content.ts — TypeScript types for course content.
 *
 * Teaches:
 * - `z.infer<typeof schema>` turns a Zod schema into a TypeScript type.
 * - `(typeof ARRAY)[number]` turns a readonly array of strings into a union type.
 * - Intersection types (`A & B`): a LessonMeta is frontmatter PLUS computed fields.
 */
import type { z } from 'zod'
import type {
  courseSchema,
  courseTranslationSchema,
  lessonFrontmatterSchema,
  LEVELS,
  ROLE_CODES,
} from '../content/schema.ts'
import type { Locale } from '../i18n/messages.ts'

export type RoleCode = (typeof ROLE_CODES)[number]
export type Level = (typeof LEVELS)[number]
export type RoleLabels = Record<RoleCode, Level>

export type Course = z.infer<typeof courseSchema>
export type CourseModule = Course['modules'][number]
export type CourseTrack = Course['tracks'][number]
export type CourseProject = Course['projects'][number]

export type CourseTranslation = z.output<typeof courseTranslationSchema>

export type LessonFrontmatter = z.output<typeof lessonFrontmatterSchema>

/** Where a lesson lives, derived from its file path. */
export type Collection = 'modules' | 'tracks' | 'projects' | 'guides'

export type LessonLocation = {
  collection: Collection
  /** Module id (m1), track id (dsa), project id (careerpilot) — or 'guides'. */
  group: string
  /** Week id (w0) or stage id (stage-1). Projects and guides have none. */
  section: string | null
  /** File name without ".md", e.g. "01-how-the-web-works". */
  slug: string
  /** Stable id, e.g. "modules/m1/w0/01-how-the-web-works". */
  id: string
  /** App URL, e.g. "/modules/m1/w0/01-how-the-web-works". */
  url: string
}

/** Everything the app knows about a lesson WITHOUT loading its full body. */
export type LessonMeta = LessonFrontmatter &
  LessonLocation & {
    filePath: string
    readingMinutes: number
    headings: string[]
    excerpt: string
    /** The language this lesson's text is in. In Indonesian mode, untranslated lessons stay 'en'. */
    language: Locale
  }

/** Languages that lessons can be translated INTO (English is the source). */
export type TranslationLocale = Exclude<Locale, 'en'>

/** What a translation file (`01-lesson.id.md`) adds on top of the English lesson. */
export type TranslationMeta = {
  locale: TranslationLocale
  /** The English lesson it translates, e.g. "modules/m4/w1/01-intro". */
  sourceId: string
  filePath: string
  sourceHash: string
  title: string
  summary: string
  readingMinutes: number
  headings: string[]
  excerpt: string
}

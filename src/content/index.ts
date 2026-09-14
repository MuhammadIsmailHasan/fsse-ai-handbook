/**
 * content/index.ts — the app's single entry point for course data.
 *
 * Components never touch files directly; they call these functions
 * (through `useContent()`, which picks the current language).
 * If we later change how content is stored, only this file changes.
 *
 * Teaches:
 * - `import.meta.glob`: Vite finds files at build time and creates imports for them.
 *   `eager: true` → included immediately; without it → loaded lazily on demand.
 *   A pattern starting with `!` excludes files.
 * - Building lookup tables (Map) once, so lookups are O(1) instead of searching arrays.
 * - Localization as an OVERLAY: the English data is complete; a translation only
 *   replaces text, and anything missing falls back to English.
 */
import type {
  Course,
  CourseTranslation,
  LessonMeta,
  TranslationLocale,
  TranslationMeta,
} from '../types/content'
import type { Locale } from '../i18n/messages'
import courseJson from '../../content/course.json'
import courseIdJson from '../../content/course.id.json'
import { courseSchema, courseTranslationSchema } from './schema'
import { stripFrontmatter, translationPathOf } from './parse'

// Validate course.json once at startup. A typo there fails loudly, not silently.
const englishCourse: Course = courseSchema.parse(courseJson)
const courseTranslations: Record<TranslationLocale, CourseTranslation> = {
  id: courseTranslationSchema.parse(courseIdJson),
}

// Small metadata for ALL English lessons (see scripts/vite-plugin-lesson-meta.ts).
const metaModules = import.meta.glob<LessonMeta>(['/content/**/*.md', '!/content/**/*.id.md'], {
  query: '?meta',
  import: 'default',
  eager: true,
})

// Translated titles, summaries and headings (small, so also eager).
const translationModules = import.meta.glob<TranslationMeta>('/content/**/*.id.md', {
  query: '?meta',
  import: 'default',
  eager: true,
})

// Full Markdown bodies (both languages), loaded only when a lesson is opened.
const bodyLoaders = import.meta.glob<string>('/content/**/*.md', {
  query: '?raw',
  import: 'default',
})

/** All English lessons, in reading order (by path: module/week, then number). */
const englishLessons: LessonMeta[] = Object.values(metaModules)
  .filter((lesson) => import.meta.env.DEV || !lesson.draft)
  .sort((a, b) => a.id.localeCompare(b.id, 'en', { numeric: true }))

const translationsById = new Map(
  Object.values(translationModules).map((t) => [`${t.locale}:${t.sourceId}`, t]),
)

function localizeLesson(lesson: LessonMeta, locale: Locale): LessonMeta {
  if (locale === 'en') return lesson
  const translation = translationsById.get(`${locale}:${lesson.id}`)
  if (!translation) return lesson // falls back to English (language stays 'en')
  const { title, summary, readingMinutes, headings, excerpt } = translation
  return { ...lesson, title, summary, readingMinutes, headings, excerpt, language: locale }
}

function localizeCourse(course: Course, t: CourseTranslation | undefined): Course {
  if (!t) return course
  return {
    ...course,
    modules: course.modules.map((m) => ({
      ...m,
      title: t.modules[m.id]?.title ?? m.title,
      summary: t.modules[m.id]?.summary ?? m.summary,
      weeks: m.weeks.map((w) => ({ ...w, ...t.modules[m.id]?.weeks?.[w.id] })),
    })),
    tracks: course.tracks.map((tr) => ({
      ...tr,
      title: t.tracks[tr.id]?.title ?? tr.title,
      summary: t.tracks[tr.id]?.summary ?? tr.summary,
      stages: tr.stages.map((s) => ({ ...s, ...t.tracks[tr.id]?.stages?.[s.id] })),
    })),
    projects: course.projects.map((p) => ({ ...p, ...t.projects[p.id] })),
    milestones: course.milestones.map((ms) => ({ ...ms, ...t.milestones[ms.id] })),
  }
}

function createContent(locale: Locale) {
  const course = locale === 'en' ? englishCourse : localizeCourse(englishCourse, courseTranslations[locale])
  const allLessons = englishLessons.map((lesson) => localizeLesson(lesson, locale))
  const lessonsById = new Map(allLessons.map((lesson) => [lesson.id, lesson]))

  const getLessonsInGroup = (collection: LessonMeta['collection'], group: string) =>
    allLessons.filter((lesson) => lesson.collection === collection && lesson.group === group)

  return {
    locale,
    course,
    allLessons,
    /** How many lessons have a translation in this language (all of them for English). */
    translatedCount: allLessons.filter((lesson) => lesson.language === locale).length,
    getLesson: (id: string) => lessonsById.get(id),
    getLessonsInGroup,
    getLessonsInSection: (
      collection: LessonMeta['collection'],
      group: string,
      section: string | null,
    ) => getLessonsInGroup(collection, group).filter((lesson) => lesson.section === section),
    /** Previous / next lesson within the same collection+group (module, track or project). */
    getNeighbors(lesson: LessonMeta) {
      const siblings = getLessonsInGroup(lesson.collection, lesson.group)
      const index = siblings.findIndex((item) => item.id === lesson.id)
      return {
        previous: index > 0 ? siblings[index - 1] : undefined,
        next: index >= 0 && index < siblings.length - 1 ? siblings[index + 1] : undefined,
      }
    },
    getModule: (id: string) => course.modules.find((m) => m.id === id),
    getTrack: (id: string) => course.tracks.find((t) => t.id === id),
    getProject: (id: string) => course.projects.find((p) => p.id === id),
  }
}

export type ContentApi = ReturnType<typeof createContent>

// Built once per language, so every component gets the SAME arrays (stable for memo/search).
const contentByLocale = new Map<Locale, ContentApi>()

export function getContent(locale: Locale): ContentApi {
  let content = contentByLocale.get(locale)
  if (!content) {
    content = createContent(locale)
    contentByLocale.set(locale, content)
  }
  return content
}

function bodyPath(lesson: LessonMeta): string {
  return lesson.language === 'en' ? lesson.filePath : translationPathOf(lesson.filePath, lesson.language)
}

export async function loadLessonBody(lesson: LessonMeta): Promise<string> {
  const path = bodyPath(lesson)
  const loader = bodyLoaders[`/${path}`]
  if (!loader) throw new Error(`No content file found for ${path}`)
  return stripFrontmatter(await loader())
}

// React's `use()` needs the SAME Promise object on every render, so we cache them.
const bodyPromises = new Map<string, Promise<string>>()

export function getLessonBodyPromise(lesson: LessonMeta): Promise<string> {
  const key = bodyPath(lesson)
  let promise = bodyPromises.get(key)
  if (!promise) {
    promise = loadLessonBody(lesson)
    bodyPromises.set(key, promise)
  }
  return promise
}

// During development, forget cached bodies when a Markdown file is edited.
if (import.meta.hot) {
  import.meta.hot.accept(() => bodyPromises.clear())
}

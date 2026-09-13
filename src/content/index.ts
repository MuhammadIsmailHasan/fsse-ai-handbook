/**
 * content/index.ts — the app's single entry point for course data.
 *
 * Components never touch files directly; they call these functions.
 * If we later change how content is stored, only this file changes.
 *
 * Teaches:
 * - `import.meta.glob`: Vite finds files at build time and creates imports for them.
 *   `eager: true` → included immediately; without it → loaded lazily on demand.
 * - Building lookup tables (Map) once, so lookups are O(1) instead of searching arrays.
 */
import type { Course, LessonMeta } from '../types/content'
import courseJson from '../../content/course.json'
import { courseSchema } from './schema'
import { stripFrontmatter } from './parse'

// Validate course.json once at startup. A typo there fails loudly, not silently.
export const course: Course = courseSchema.parse(courseJson)

// Small metadata for ALL lessons (see scripts/vite-plugin-lesson-meta.ts).
const metaModules = import.meta.glob<LessonMeta>('/content/**/*.md', {
  query: '?meta',
  import: 'default',
  eager: true,
})

// Full Markdown bodies, loaded only when a lesson is opened.
const bodyLoaders = import.meta.glob<string>('/content/**/*.md', {
  query: '?raw',
  import: 'default',
})

/** All lessons, in reading order (by path, which starts with the module/week and a number). */
export const allLessons: LessonMeta[] = Object.values(metaModules)
  .filter((lesson) => import.meta.env.DEV || !lesson.draft)
  .sort((a, b) => a.id.localeCompare(b.id, 'en', { numeric: true }))

const lessonsById = new Map(allLessons.map((lesson) => [lesson.id, lesson]))

export function getLesson(id: string): LessonMeta | undefined {
  return lessonsById.get(id)
}

export function getLessonsInSection(
  collection: LessonMeta['collection'],
  group: string,
  section: string | null,
): LessonMeta[] {
  return allLessons.filter(
    (lesson) =>
      lesson.collection === collection && lesson.group === group && lesson.section === section,
  )
}

export function getLessonsInGroup(collection: LessonMeta['collection'], group: string) {
  return allLessons.filter((lesson) => lesson.collection === collection && lesson.group === group)
}

export async function loadLessonBody(lesson: LessonMeta): Promise<string> {
  const loader = bodyLoaders[`/${lesson.filePath}`]
  if (!loader) throw new Error(`No content file found for ${lesson.filePath}`)
  return stripFrontmatter(await loader())
}

// React's `use()` needs the SAME Promise object on every render, so we cache them.
const bodyPromises = new Map<string, Promise<string>>()

export function getLessonBodyPromise(lesson: LessonMeta): Promise<string> {
  let promise = bodyPromises.get(lesson.id)
  if (!promise) {
    promise = loadLessonBody(lesson)
    bodyPromises.set(lesson.id, promise)
  }
  return promise
}

// During development, forget cached bodies when a Markdown file is edited.
if (import.meta.hot) {
  import.meta.hot.accept(() => bodyPromises.clear())
}

/** Previous / next lesson within the same collection+group (module, track or project). */
export function getNeighbors(lesson: LessonMeta) {
  const siblings = getLessonsInGroup(lesson.collection, lesson.group)
  const index = siblings.findIndex((item) => item.id === lesson.id)
  return {
    previous: index > 0 ? siblings[index - 1] : undefined,
    next: index >= 0 && index < siblings.length - 1 ? siblings[index + 1] : undefined,
  }
}

export const getModule = (id: string) => course.modules.find((m) => m.id === id)
export const getTrack = (id: string) => course.tracks.find((t) => t.id === id)
export const getProject = (id: string) => course.projects.find((p) => p.id === id)

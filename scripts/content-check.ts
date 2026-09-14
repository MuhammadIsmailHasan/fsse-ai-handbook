/**
 * content-check.ts — validates ALL content before you commit.
 *
 *   npm run content:check
 *
 * Checks:
 * 1. Every .md file has valid frontmatter and lives in the right folder.
 * 2. Every lesson's module/week, track/stage or project exists in course.json.
 * 3. Every `:::exercise{path="..."}` points to a folder that exists.
 * 4. Every internal link like `[text](/modules/m1/w0/01-x)` points to a real page.
 * 5. Every translation (`01-x.id.md`) has an English source, is up to date with it
 *    (sourceHash), and keeps the same structure: directives, code, links.
 * 6. `course.id.json` only translates modules/weeks/tracks/projects that exist.
 *
 * Teaches: writing a small CLI tool in TypeScript with Node's fs/path modules,
 * collecting ALL errors (not stopping at the first), and exit codes
 * (0 = success, 1 = failure — CI pipelines rely on this).
 */
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs'
import path from 'node:path'
import {
  buildLessonMeta,
  buildTranslationMeta,
  isTranslationPath,
  sourcePathOf,
  stripFrontmatter,
} from '../src/content/parse.ts'
import { courseSchema, courseTranslationSchema } from '../src/content/schema.ts'
import { compareStructure } from '../src/content/translation.ts'
import type { LessonMeta, TranslationMeta } from '../src/types/content.ts'
import { sourceHash } from './i18n-hash.ts'

const ROOT = process.cwd()
const errors: string[] = []

function walk(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const full = path.join(dir, name)
    return statSync(full).isDirectory() ? walk(full) : [full]
  })
}

const toRelative = (file: string) => path.relative(ROOT, file).split(path.sep).join('/')

// 1. course.json
const courseResult = courseSchema.safeParse(
  JSON.parse(readFileSync(path.join(ROOT, 'content/course.json'), 'utf8')),
)
if (!courseResult.success) {
  console.error('❌ content/course.json is invalid:\n', courseResult.error.issues)
  process.exit(1)
}
const course = courseResult.data

// 2. Lessons (English sources) and their translations
const files = walk(path.join(ROOT, 'content')).filter((file) => file.endsWith('.md'))
const lessons: { meta: LessonMeta; body: string }[] = []
const translations: { meta: TranslationMeta; body: string }[] = []

for (const file of files) {
  const relative = toRelative(file)
  const source = readFileSync(file, 'utf8')
  try {
    if (isTranslationPath(relative)) {
      translations.push({
        meta: buildTranslationMeta(relative, source),
        body: stripFrontmatter(source),
      })
    } else {
      lessons.push({ meta: buildLessonMeta(relative, source), body: stripFrontmatter(source) })
    }
  } catch (error) {
    errors.push((error as Error).message)
  }
}

const knownUrls = new Set(lessons.map(({ meta }) => meta.url))
const staticUrls = ['/', '/roadmap', '/schedule', '/settings', '/tracks/dsa/review']
for (const url of staticUrls) knownUrls.add(url)
for (const m of course.modules) knownUrls.add(`/modules/${m.id}`)
for (const t of course.tracks) knownUrls.add(`/tracks/${t.id}`)
for (const p of course.projects) knownUrls.add(`/projects/${p.id}`)

const problemIds = new Map<string, string>()

for (const { meta, body } of lessons) {
  const where = meta.filePath

  // Structure references
  if (meta.collection === 'modules') {
    const module = course.modules.find((m) => m.id === meta.group)
    if (!module) errors.push(`${where}\n  Module "${meta.group}" is not in course.json`)
    else if (!module.weeks.some((w) => w.id === meta.section)) {
      errors.push(
        `${where}\n  Week "${meta.section}" is not in module "${meta.group}" in course.json`,
      )
    }
  }
  if (meta.collection === 'tracks') {
    const track = course.tracks.find((t) => t.id === meta.group)
    if (!track) errors.push(`${where}\n  Track "${meta.group}" is not in course.json`)
    else if (!track.stages.some((s) => s.id === meta.section)) {
      errors.push(
        `${where}\n  Stage "${meta.section}" is not in track "${meta.group}" in course.json`,
      )
    }
  }
  if (meta.collection === 'projects' && !course.projects.some((p) => p.id === meta.group)) {
    errors.push(`${where}\n  Project "${meta.group}" is not in course.json`)
  }

  // Exercise & problem folders
  for (const match of body.matchAll(/:{3,}(?:exercise|problem)\{[^}]*path="([^"]+)"/g)) {
    const exercisePath = match[1]!
    if (!existsSync(path.join(ROOT, exercisePath))) {
      errors.push(`${where}\n  Exercise folder not found: ${exercisePath}`)
    }
  }

  // Problem ids must be unique across the whole handbook (they key the review queue)
  for (const match of body.matchAll(/:{3,}problem\{[^}]*id="([^"]+)"/g)) {
    const id = match[1]!
    const firstSeen = problemIds.get(id)
    if (firstSeen) errors.push(`${where}\n  Duplicate problem id "${id}" (also in ${firstSeen})`)
    else problemIds.set(id, where)
  }

  // Internal links (ignore #anchors)
  for (const match of body.matchAll(/\]\((\/[^)\s#]*)(#[^)\s]*)?\)/g)) {
    const url = match[1]!.replace(/\/$/, '') || '/'
    if (!knownUrls.has(url)) errors.push(`${where}\n  Broken internal link: ${url}`)
  }
}

// 5. Translations
const lessonsByPath = new Map(lessons.map((lesson) => [lesson.meta.filePath, lesson]))

for (const { meta, body } of translations) {
  const where = meta.filePath
  const englishPath = sourcePathOf(meta.filePath)
  const english = lessonsByPath.get(englishPath)
  if (!english) {
    errors.push(`${where}\n  No English lesson at ${englishPath}`)
    continue
  }

  const expectedHash = sourceHash(readFileSync(path.join(ROOT, englishPath), 'utf8'))
  if (meta.sourceHash !== expectedHash) {
    errors.push(
      `${where}\n  Stale translation: ${englishPath} changed since it was translated.\n` +
        `  Update the translation, then run: npm run i18n -- stamp ${where}`,
    )
  }

  for (const problem of compareStructure(english.body, body)) {
    errors.push(`${where}\n  ${problem}`)
  }

  for (const match of body.matchAll(/\]\((\/[^)\s#]*)(#[^)\s]*)?\)/g)) {
    const url = match[1]!.replace(/\/$/, '') || '/'
    if (!knownUrls.has(url)) errors.push(`${where}\n  Broken internal link: ${url}`)
  }
}

// 6. course.id.json
const courseIdPath = path.join(ROOT, 'content/course.id.json')
if (existsSync(courseIdPath)) {
  const result = courseTranslationSchema.safeParse(JSON.parse(readFileSync(courseIdPath, 'utf8')))
  if (!result.success) {
    errors.push(`content/course.id.json is invalid:\n  ${JSON.stringify(result.error.issues)}`)
  } else {
    const t = result.data
    const where = 'content/course.id.json'
    for (const [id, m] of Object.entries(t.modules)) {
      const module = course.modules.find((x) => x.id === id)
      if (!module) errors.push(`${where}\n  Unknown module "${id}"`)
      for (const weekId of Object.keys(m.weeks ?? {})) {
        if (module && !module.weeks.some((w) => w.id === weekId)) {
          errors.push(`${where}\n  Unknown week "${id}/${weekId}"`)
        }
      }
    }
    for (const [id, tr] of Object.entries(t.tracks)) {
      const track = course.tracks.find((x) => x.id === id)
      if (!track) errors.push(`${where}\n  Unknown track "${id}"`)
      for (const stageId of Object.keys(tr.stages ?? {})) {
        if (track && !track.stages.some((st) => st.id === stageId)) {
          errors.push(`${where}\n  Unknown stage "${id}/${stageId}"`)
        }
      }
    }
    for (const id of Object.keys(t.projects)) {
      if (!course.projects.some((p) => p.id === id))
        errors.push(`${where}\n  Unknown project "${id}"`)
    }
    for (const id of Object.keys(t.milestones)) {
      if (!course.milestones.some((m) => m.id === id)) {
        errors.push(`${where}\n  Unknown milestone "${id}"`)
      }
    }
  }
}

// Report
if (errors.length > 0) {
  console.error(`\n❌ Found ${errors.length} problem(s):\n`)
  for (const error of errors) console.error(`• ${error}\n`)
  process.exit(1)
}

console.log(
  `✅ Content OK — ${lessons.length} lesson(s) and ${translations.length} translation(s) checked.`,
)

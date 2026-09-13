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
 *
 * Teaches: writing a small CLI tool in TypeScript with Node's fs/path modules,
 * collecting ALL errors (not stopping at the first), and exit codes
 * (0 = success, 1 = failure — CI pipelines rely on this).
 */
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs'
import path from 'node:path'
import { buildLessonMeta, stripFrontmatter } from '../src/content/parse.ts'
import { courseSchema } from '../src/content/schema.ts'
import type { LessonMeta } from '../src/types/content.ts'

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

// 2. Lessons
const files = walk(path.join(ROOT, 'content')).filter((file) => file.endsWith('.md'))
const lessons: { meta: LessonMeta; body: string }[] = []

for (const file of files) {
  const relative = toRelative(file)
  const source = readFileSync(file, 'utf8')
  try {
    lessons.push({ meta: buildLessonMeta(relative, source), body: stripFrontmatter(source) })
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

// Report
if (errors.length > 0) {
  console.error(`\n❌ Found ${errors.length} problem(s):\n`)
  for (const error of errors) console.error(`• ${error}\n`)
  process.exit(1)
}

console.log(`✅ Content OK — ${lessons.length} file(s) checked.`)

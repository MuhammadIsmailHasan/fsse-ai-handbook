/**
 * parse.ts — turns a Markdown file (path + text) into validated LessonMeta.
 *
 * Used in three places:
 * 1. the Vite plugin (build time, for the app),
 * 2. `npm run content:check` (a script),
 * 3. unit tests.
 *
 * Teaches:
 * - Pure functions: same input → same output, no side effects → easy to test.
 * - Throwing errors with helpful messages (file path + what's wrong).
 * - Regular expressions for simple parsing.
 */
import { parse as parseYaml } from 'yaml'
import { z } from 'zod'
import type { LessonLocation, LessonMeta, TranslationMeta } from '../types/content.ts'
import { lessonFrontmatterSchema, translationFrontmatterSchema } from './schema.ts'

export class ContentError extends Error {
  constructor(filePath: string, detail: string) {
    super(`[content] ${filePath}\n${detail}`)
    this.name = 'ContentError'
  }
}

const FRONTMATTER_RE = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/

/** Splits "---\nyaml\n---\nbody" into its two parts. */
export function splitFrontmatter(source: string): { yaml: string; body: string } | null {
  const match = FRONTMATTER_RE.exec(source)
  if (!match) return null
  return { yaml: match[1] ?? '', body: source.slice(match[0].length) }
}

/** Removes the frontmatter block, returning only the Markdown body. */
export function stripFrontmatter(source: string): string {
  return splitFrontmatter(source)?.body ?? source
}

const SLUG_RE = /^[a-z0-9][a-z0-9-]*$/

/**
 * Works out where a lesson belongs from its path (relative to the project root):
 *   content/modules/m1/w0/01-intro.md    → module lesson
 *   content/tracks/dsa/stage-1/01-big-o.md → track lesson
 *   content/projects/careerpilot/01-brief.md → project page
 *   content/guides/how-to-study.md       → guide
 */
export function parseLessonPath(filePath: string): LessonLocation {
  const normalized = filePath.replace(/\\/g, '/').replace(/^\/+/, '')
  const parts = normalized.split('/')

  if (parts[0] !== 'content' || !normalized.endsWith('.md')) {
    throw new ContentError(filePath, 'Lesson files must live in content/ and end with .md')
  }

  const fileName = parts.at(-1)!.replace(/\.md$/, '')
  if (!SLUG_RE.test(fileName)) {
    throw new ContentError(
      filePath,
      'File names must be lowercase letters, numbers and dashes, e.g. 01-how-the-web-works.md',
    )
  }

  const [, collection, group, section] = parts
  const depth = parts.length

  if ((collection === 'modules' || collection === 'tracks') && depth === 5) {
    const id = `${collection}/${group}/${section}/${fileName}`
    return { collection, group: group!, section: section!, slug: fileName, id, url: `/${id}` }
  }
  if (collection === 'projects' && depth === 4) {
    const id = `projects/${group}/${fileName}`
    return { collection, group: group!, section: null, slug: fileName, id, url: `/${id}` }
  }
  if (collection === 'guides' && depth === 3) {
    const id = `guides/${fileName}`
    return { collection, group: 'guides', section: null, slug: fileName, id, url: `/${id}` }
  }

  throw new ContentError(
    filePath,
    'Unexpected location. Use content/modules/<module>/<week>/<file>.md, ' +
      'content/tracks/<track>/<stage>/<file>.md, content/projects/<project>/<file>.md ' +
      'or content/guides/<file>.md',
  )
}

const WORDS_PER_MINUTE = 220

/** Very small Markdown → plain text, good enough for search and word counts. */
export function markdownToPlainText(markdown: string): string {
  return markdown
    .replace(/```[\s\S]*?```/g, ' ') // code blocks
    .replace(/`([^`]*)`/g, '$1') // inline code
    .replace(/!\[[^\]]*\]\([^)]*\)/g, ' ') // images
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1') // links → their text
    .replace(/^:{2,}.*$/gm, ' ') // directive fences (:::tip, ::part[...])
    .replace(/:[a-z]+\[([^\]]*)\](\{[^}]*\})?/g, '$1') // text directives → label
    .replace(/[#>*_|~-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

/** Reads and validates the frontmatter block with any Zod schema. */
function parseFrontmatter<T extends z.ZodType>(filePath: string, source: string, schema: T) {
  const parts = splitFrontmatter(source)
  if (!parts) {
    throw new ContentError(filePath, 'Missing frontmatter. The file must start with a --- block.')
  }

  let data: unknown
  try {
    data = parseYaml(parts.yaml)
  } catch (error) {
    throw new ContentError(filePath, `Invalid YAML in frontmatter: ${(error as Error).message}`)
  }

  const result = schema.safeParse(data)
  if (!result.success) {
    throw new ContentError(filePath, z.prettifyError(result.error))
  }
  return { data: result.data as z.output<T>, body: parts.body }
}

/** Reading time, headings and excerpt — the same for any language. */
function bodyStats(body: string) {
  const plain = markdownToPlainText(body)
  const wordCount = plain ? plain.split(' ').length : 0
  return {
    readingMinutes: Math.max(1, Math.round(wordCount / WORDS_PER_MINUTE)),
    headings: [...body.matchAll(/^#{2,3}\s+(.+)$/gm)].map((m) => markdownToPlainText(m[1] ?? '')),
    excerpt: plain.slice(0, 280),
  }
}

export function buildLessonMeta(filePath: string, source: string): LessonMeta {
  if (isTranslationPath(filePath)) {
    throw new ContentError(filePath, 'This is a translation file; use buildTranslationMeta().')
  }
  const location = parseLessonPath(filePath)
  const { data, body } = parseFrontmatter(filePath, source, lessonFrontmatterSchema)

  return { ...data, ...location, filePath, ...bodyStats(body), language: 'en' }
}

// ── Translations ─────────────────────────────────────────────────────────────
//   content/modules/m4/w1/01-intro.md     ← English (the source of truth)
//   content/modules/m4/w1/01-intro.id.md  ← Bahasa Indonesia

const TRANSLATION_RE = /\.(id)\.md$/

export function isTranslationPath(filePath: string): boolean {
  return TRANSLATION_RE.test(filePath)
}

/** "01-intro.id.md" → "01-intro.md" */
export function sourcePathOf(translationPath: string): string {
  return translationPath.replace(TRANSLATION_RE, '.md')
}

/** "01-intro.md" + "id" → "01-intro.id.md" */
export function translationPathOf(sourcePath: string, locale: TranslationMeta['locale']): string {
  return sourcePath.replace(/\.md$/, `.${locale}.md`)
}

export function buildTranslationMeta(filePath: string, source: string): TranslationMeta {
  const match = TRANSLATION_RE.exec(filePath)
  if (!match) throw new ContentError(filePath, 'Translation files must end with .id.md')
  const location = parseLessonPath(sourcePathOf(filePath))
  const { data, body } = parseFrontmatter(filePath, source, translationFrontmatterSchema)

  return {
    locale: match[1] as TranslationMeta['locale'],
    sourceId: location.id,
    filePath,
    sourceHash: data.sourceHash,
    title: data.title,
    summary: data.summary,
    ...bodyStats(body),
  }
}

/**
 * The English text a translation must follow: title, summary and body.
 * (Roles, tags, duration… are NOT included — changing them doesn't need re-translation.)
 * Scripts hash this to detect stale translations.
 */
export function translatableText(source: string): string {
  const parts = splitFrontmatter(source)
  if (!parts) return source
  const data = (parseYaml(parts.yaml) ?? {}) as { title?: unknown; summary?: unknown }
  return `${String(data.title ?? '')}\n${String(data.summary ?? '')}\n${parts.body.trim()}\n`
}

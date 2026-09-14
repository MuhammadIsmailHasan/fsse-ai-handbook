/**
 * vite-plugin-lesson-meta.ts — a tiny custom Vite plugin.
 *
 * Problem: the sidebar and search need every lesson's title, roles, etc.
 * If we bundled every full lesson into the app, the first page load would be huge.
 *
 * Solution: importing a Markdown file with the `?meta` query returns ONLY its
 * validated metadata (small). The full body is loaded lazily with `?raw` when
 * you open the lesson.
 *
 *   import.meta.glob('/content/**\/*.md', { query: '?meta', eager: true })  → metadata
 *   import.meta.glob('/content/**\/*.md', { query: '?raw' })               → bodies, on demand
 *
 * Teaches: Vite/Rollup plugin hooks (`load`), and failing the build early when
 * content is invalid (errors show up in the browser overlay during `npm run dev`).
 */
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import type { Plugin } from 'vite'
import { buildLessonMeta, buildTranslationMeta, isTranslationPath } from '../src/content/parse.ts'

const META_QUERY = '?meta'

export function lessonMetaPlugin(): Plugin {
  let root = process.cwd()

  return {
    name: 'fsse:lesson-meta',
    enforce: 'pre',

    configResolved(config) {
      root = config.root
    },

    async load(id) {
      if (!id.endsWith(`.md${META_QUERY}`)) return null

      const absolutePath = id.slice(0, -META_QUERY.length)
      // Tell Vite to re-run this when the file changes (hot reload).
      this.addWatchFile(absolutePath)

      const source = await readFile(absolutePath, 'utf8')
      const relativePath = path.relative(root, absolutePath).split(path.sep).join('/')
      // Translations (01-lesson.id.md) return only their translated text + stats.
      const meta = isTranslationPath(relativePath)
        ? buildTranslationMeta(relativePath, source)
        : buildLessonMeta(relativePath, source)

      return `export default ${JSON.stringify(meta)}`
    },
  }
}

/**
 * i18n.ts — translation helper.
 *
 *   npm run i18n                      → coverage per module/track + stale translations
 *   npm run i18n -- stamp <file.id.md> → record that the translation matches the current English
 *   npm run i18n -- stamp --all       → stamp every translation (only after reviewing them!)
 *
 * Teaches: a tiny CLI with subcommands, and editing YAML frontmatter in place
 * without re-serializing (so formatting and comments stay untouched).
 */
import { readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs'
import path from 'node:path'
import { isTranslationPath, sourcePathOf, splitFrontmatter } from '../src/content/parse.ts'
import { sourceHash } from './i18n-hash.ts'

const ROOT = process.cwd()
const toRelative = (file: string) => path.relative(ROOT, file).split(path.sep).join('/')

function walk(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const full = path.join(dir, name)
    return statSync(full).isDirectory() ? walk(full) : [full]
  })
}

const allFiles = walk(path.join(ROOT, 'content'))
  .filter((file) => file.endsWith('.md'))
  .map(toRelative)
const translations = allFiles.filter(isTranslationPath)
const sources = allFiles.filter((file) => !isTranslationPath(file))

function currentHash(translationPath: string): string | undefined {
  const parts = splitFrontmatter(readFileSync(path.join(ROOT, translationPath), 'utf8'))
  return /^sourceHash:\s*"?([0-9a-f]+)"?\s*$/m.exec(parts?.yaml ?? '')?.[1]
}

function expectedHash(translationPath: string): string {
  return sourceHash(readFileSync(path.join(ROOT, sourcePathOf(translationPath)), 'utf8'))
}

function stamp(translationPath: string) {
  const file = path.join(ROOT, translationPath)
  const text = readFileSync(file, 'utf8')
  const parts = splitFrontmatter(text)
  if (!parts) throw new Error(`${translationPath}: missing frontmatter`)
  const hash = expectedHash(translationPath)
  const yaml = /^sourceHash:.*$/m.test(parts.yaml)
    ? parts.yaml.replace(/^sourceHash:.*$/m, `sourceHash: ${hash}`)
    : `${parts.yaml}\nsourceHash: ${hash}`
  writeFileSync(file, `---\n${yaml}\n---\n${parts.body}`)
  console.log(`✔ ${translationPath} → ${hash}`)
}

const [command, ...args] = process.argv.slice(2)

if (command === 'stamp') {
  const targets = args.includes('--all') ? translations : args
  if (targets.length === 0) {
    console.error('Usage: npm run i18n -- stamp <file.id.md> [...] | --all')
    process.exit(1)
  }
  for (const target of targets) {
    if (!isTranslationPath(target)) {
      console.error(`✖ ${target} is not a .id.md file`)
      process.exit(1)
    }
    stamp(target)
  }
} else {
  // Coverage report, grouped by module / track / project folder.
  const groups = new Map<string, { total: number; translated: number }>()
  const translated = new Set(translations.map(sourcePathOf))
  for (const source of sources) {
    const group = source.split('/').slice(1, 3).join('/') // modules/m4, tracks/dsa, guides/x.md
    const key = group.endsWith('.md') ? 'guides' : group
    const entry = groups.get(key) ?? { total: 0, translated: 0 }
    entry.total++
    if (translated.has(source)) entry.translated++
    groups.set(key, entry)
  }

  console.log('Bahasa Indonesia coverage\n')
  for (const [group, { total, translated: done }] of [...groups].sort()) {
    const bar = '█'.repeat(Math.round((done / total) * 20)).padEnd(20, '░')
    console.log(`  ${group.padEnd(28)} ${bar} ${String(done).padStart(3)}/${total}`)
  }
  console.log(`\n  Total: ${translated.size}/${sources.length} lessons`)

  const stale = translations.filter((t) => currentHash(t) !== expectedHash(t))
  if (stale.length) {
    console.log('\n⚠️  Stale (English changed since translation):')
    for (const file of stale) console.log(`  • ${file}`)
  }
}

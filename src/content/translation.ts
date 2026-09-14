/**
 * translation.ts — checks that a translated lesson has the same SHAPE as the English one.
 *
 * A translation should change words, never structure. So we compare:
 * - directives (::part, :::exercise{path}, :::quiz…) — same order, same attributes
 *   (except `title`, which is display text and may be translated),
 * - code blocks — same order and language; real code must be byte-for-byte identical
 *   (only ```mermaid and ```text / plain blocks may be translated),
 * - internal links — the same set of pages.
 *
 * Teaches: comparing two documents by extracting a "signature" from each —
 * simpler and more robust than diffing the raw text.
 */

export type CodeBlock = { lang: string; code: string }

export type Structure = {
  directives: string[]
  codeBlocks: CodeBlock[]
  links: string[]
}

/** Code blocks whose content is prose-like and may be translated. */
const TRANSLATABLE_CODE = new Set(['mermaid', 'text', ''])

const FENCE_OPEN = /^\s*(`{3,}|~{3,})\s*([^\s`]*)/
const DIRECTIVE = /^\s*(:{2,})([a-zA-Z][\w-]*)(?:\[[^\]]*\])?(?:\{([^}]*)\})?/
const ATTRIBUTE = /([a-zA-Z][\w-]*)="([^"]*)"/g
const INTERNAL_LINK = /\]\((\/[^)\s#]*)(?:#[^)\s]*)?\)/g

export function extractStructure(body: string): Structure {
  const directives: string[] = []
  const codeBlocks: CodeBlock[] = []
  const prose: string[] = []

  let fence: { marker: string; lang: string; lines: string[] } | null = null

  for (const line of body.split('\n')) {
    if (fence) {
      const closing = line.trim()
      if (
        closing.length >= fence.marker.length &&
        closing === closing[0]!.repeat(closing.length) &&
        closing[0] === fence.marker[0]
      ) {
        codeBlocks.push({ lang: fence.lang, code: fence.lines.join('\n') })
        fence = null
      } else {
        fence.lines.push(line)
      }
      continue
    }

    const open = FENCE_OPEN.exec(line)
    if (open) {
      fence = { marker: open[1]!, lang: (open[2] ?? '').toLowerCase(), lines: [] }
      continue
    }

    prose.push(line)
    const directive = DIRECTIVE.exec(line)
    if (directive) {
      const attributes = [...(directive[3] ?? '').matchAll(ATTRIBUTE)]
        .filter(([, name]) => name !== 'title')
        .map(([, name, value]) => `${name}=${value}`)
        .sort()
      directives.push(`${directive[1]}${directive[2]}{${attributes.join(' ')}}`)
    }
  }

  const links = [...new Set([...prose.join('\n').matchAll(INTERNAL_LINK)].map((m) => m[1]!))]
  return { directives, codeBlocks, links: links.sort() }
}

/** Returns human-readable problems; an empty array means the shapes match. */
export function compareStructure(sourceBody: string, translatedBody: string): string[] {
  const source = extractStructure(sourceBody)
  const translated = extractStructure(translatedBody)
  const problems: string[] = []

  const directiveCount = Math.max(source.directives.length, translated.directives.length)
  for (let i = 0; i < directiveCount; i++) {
    if (source.directives[i] !== translated.directives[i]) {
      problems.push(
        `Directive #${i + 1} differs: English "${source.directives[i] ?? '(none)'}" vs translation "${translated.directives[i] ?? '(none)'}"`,
      )
      break // later directives are usually shifted too — one message is enough
    }
  }

  if (source.codeBlocks.length !== translated.codeBlocks.length) {
    problems.push(
      `Code block count differs: English ${source.codeBlocks.length} vs translation ${translated.codeBlocks.length}`,
    )
  } else {
    source.codeBlocks.forEach((block, i) => {
      const other = translated.codeBlocks[i]!
      if (block.lang !== other.lang) {
        problems.push(`Code block #${i + 1} language differs: "${block.lang}" vs "${other.lang}"`)
      } else if (!TRANSLATABLE_CODE.has(block.lang) && block.code !== other.code) {
        problems.push(
          `Code block #${i + 1} (${block.lang}) was changed — keep code identical to English`,
        )
      }
    })
  }

  const missing = source.links.filter((link) => !translated.links.includes(link))
  const extra = translated.links.filter((link) => !source.links.includes(link))
  if (missing.length) problems.push(`Internal links missing: ${missing.join(', ')}`)
  if (extra.length) problems.push(`Internal links not in English: ${extra.join(', ')}`)

  return problems
}

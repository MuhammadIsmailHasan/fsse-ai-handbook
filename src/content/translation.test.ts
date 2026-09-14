/**
 * translation.test.ts — translated lessons must keep the English structure.
 */
import { describe, expect, it } from 'vitest'
import { buildTranslationMeta, isTranslationPath, sourcePathOf, translationPathOf } from './parse.ts'
import { compareStructure, extractStructure } from './translation.ts'

const english = `
::part[Learn the Concept]{n="1"}

## What is a route?

A route maps a URL to a function. See [Flask basics](/modules/m2/w4/01-flask).

:::exercise{path="exercises/m4/w1/01-hello" ai="no-ai" title="Say hello"}
Write it.
:::

\`\`\`python
def hello():
    return "hi"  # greet
\`\`\`

\`\`\`mermaid
flowchart LR
  Browser --> Server
\`\`\`
`

const indonesian = `
::part[Pelajari Konsepnya]{n="1"}

## Apa itu route?

Route memetakan URL ke sebuah fungsi. Lihat [dasar Flask](/modules/m2/w4/01-flask).

:::exercise{path="exercises/m4/w1/01-hello" ai="no-ai" title="Menyapa"}
Tulis kodenya.
:::

\`\`\`python
def hello():
    return "hi"  # greet
\`\`\`

\`\`\`mermaid
flowchart LR
  Browser --> Server[Server kita]
\`\`\`
`

describe('translation paths', () => {
  it('maps between English and Indonesian files', () => {
    expect(isTranslationPath('content/modules/m4/w1/01-intro.id.md')).toBe(true)
    expect(isTranslationPath('content/modules/m4/w1/01-intro.md')).toBe(false)
    expect(sourcePathOf('content/modules/m4/w1/01-intro.id.md')).toBe(
      'content/modules/m4/w1/01-intro.md',
    )
    expect(translationPathOf('content/guides/how-to-study.md', 'id')).toBe(
      'content/guides/how-to-study.id.md',
    )
  })

  it('builds translation metadata pointing at the English lesson', () => {
    const meta = buildTranslationMeta(
      'content/modules/m4/w1/01-intro.id.md',
      `---\ntitle: Pengenalan\nsummary: Ringkasan singkat.\nsourceHash: 0123456789ab\n---\n## Halo\n`,
    )
    expect(meta.sourceId).toBe('modules/m4/w1/01-intro')
    expect(meta.locale).toBe('id')
    expect(meta.headings).toEqual(['Halo'])
  })

  it('rejects translations that repeat English-only fields', () => {
    expect(() =>
      buildTranslationMeta(
        'content/modules/m4/w1/01-intro.id.md',
        `---\ntitle: X\nsummary: Y\nsourceHash: 0123456789ab\ndurationMinutes: 60\n---\n`,
      ),
    ).toThrow(/durationMinutes/)
  })
})

describe('compareStructure', () => {
  it('accepts a faithful translation (titles, prose and mermaid labels may change)', () => {
    expect(compareStructure(english, indonesian)).toEqual([])
  })

  it('ignores directive-like lines inside code blocks', () => {
    const body = '```markdown\n:::quiz\n```\n'
    expect(extractStructure(body).directives).toEqual([])
  })

  it('reports a changed exercise path', () => {
    const broken = indonesian.replace('01-hello', '02-hello')
    expect(compareStructure(english, broken)[0]).toMatch(/Directive #2 differs/)
  })

  it('reports edited code', () => {
    const broken = indonesian.replace('# greet', '# sapa')
    expect(compareStructure(english, broken)).toEqual([
      'Code block #1 (python) was changed — keep code identical to English',
    ])
  })

  it('reports missing blocks and links', () => {
    const broken = indonesian.replace(/```mermaid[\s\S]*?```/, '').replace('(/modules/m2/w4/01-flask)', '')
    const problems = compareStructure(english, broken)
    expect(problems).toContain('Code block count differs: English 2 vs translation 1')
    expect(problems).toContain('Internal links missing: /modules/m2/w4/01-flask')
  })
})

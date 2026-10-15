/**
 * parse.test.ts — unit tests for the content parser.
 *
 * Teaches: the Arrange → Act → Assert pattern, and testing error cases too.
 * Run with: npm test
 */
import { describe, expect, it } from 'vitest'
import { buildLessonMeta, markdownToPlainText, parseLessonPath, stripFrontmatter } from './parse.ts'

const validFrontmatter = `---
title: How the Web Works
summary: What happens between typing a URL and seeing a page.
type: lesson
source: core
roles: { be: core, fe: core, fs: core, ai: core, ops: core }
durationMinutes: 120
---
`

describe('parseLessonPath', () => {
  it('parses a module lesson path', () => {
    expect(parseLessonPath('content/modules/m1/w0/01-how-the-web-works.md')).toEqual({
      collection: 'modules',
      group: 'm1',
      section: 'w0',
      slug: '01-how-the-web-works',
      id: 'modules/m1/w0/01-how-the-web-works',
      url: '/modules/m1/w0/01-how-the-web-works',
    })
  })

  it('parses project and guide paths (no section)', () => {
    expect(parseLessonPath('content/projects/careerpilot/01-brief.md').section).toBeNull()
    expect(parseLessonPath('content/guides/how-to-study.md').url).toBe('/guides/how-to-study')
  })

  it('rejects bad file names and locations', () => {
    expect(() => parseLessonPath('content/modules/m1/w0/My Lesson.md')).toThrow(/lowercase/)
    expect(() => parseLessonPath('content/modules/m1/lesson.md')).toThrow(/Unexpected location/)
  })
})

describe('buildLessonMeta', () => {
  it('builds metadata from valid frontmatter', () => {
    const source = `${validFrontmatter}\n## 🎯 What you'll learn\n\nSome **text** here.\n`
    const meta = buildLessonMeta('content/modules/m1/w0/01-how-the-web-works.md', source)

    expect(meta.title).toBe('How the Web Works')
    expect(meta.tags).toEqual([]) // default applied
    expect(meta.draft).toBe(false)
    expect(meta.headings).toEqual(["🎯 What you'll learn"])
    expect(meta.readingMinutes).toBeGreaterThanOrEqual(1)
  })

  it('rejects an unknown source value', () => {
    const source = validFrontmatter.replace('source: core', 'source: elsewhere')
    expect(() => buildLessonMeta('content/modules/m1/w0/01-a.md', source)).toThrow(/source/)
  })

  it('reports unknown fields (typos)', () => {
    const source = validFrontmatter.replace('durationMinutes', 'durationMinute')
    expect(() => buildLessonMeta('content/modules/m1/w0/01-a.md', source)).toThrow()
  })

  it('fails without frontmatter', () => {
    expect(() => buildLessonMeta('content/guides/a.md', '# Hello')).toThrow(/Missing frontmatter/)
  })
})

describe('helpers', () => {
  it('strips frontmatter', () => {
    expect(stripFrontmatter(`${validFrontmatter}Body`)).toBe('Body')
  })

  it('converts markdown to plain text', () => {
    expect(markdownToPlainText('A [link](http://x.dev) and `code` and :term[API]{bahasa="x"}')).toBe(
      'A link and code and API',
    )
  })
})

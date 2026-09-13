/**
 * highlighter.ts — syntax highlighting for code blocks, powered by Shiki.
 *
 * Teaches:
 * - Lazy singletons: create the (expensive) highlighter only once, on first use,
 *   and share the same Promise with every caller.
 * - Dual themes: Shiki outputs CSS variables for light AND dark colors;
 *   CSS in index.css picks one based on the `.dark` class.
 */
import { createHighlighter, type Highlighter } from 'shiki'

const LANGUAGES = [
  'python',
  'typescript',
  'tsx',
  'javascript',
  'jsx',
  'bash',
  'sql',
  'json',
  'yaml',
  'html',
  'css',
  'dockerfile',
  'toml',
  'diff',
  'markdown',
  'ini',
  'hcl',
  'http',
] as const

let highlighterPromise: Promise<Highlighter> | null = null

function getHighlighter() {
  highlighterPromise ??= createHighlighter({
    themes: ['github-light', 'github-dark'],
    langs: [...LANGUAGES],
  })
  return highlighterPromise
}

export async function highlightCode(code: string, language: string): Promise<string> {
  const highlighter = await getHighlighter()
  const lang = highlighter.getLoadedLanguages().includes(language) ? language : 'text'
  return highlighter.codeToHtml(code, {
    lang,
    themes: { light: 'github-light', dark: 'github-dark' },
    defaultColor: false,
  })
}

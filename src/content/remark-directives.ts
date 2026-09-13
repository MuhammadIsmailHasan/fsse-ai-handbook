/**
 * remark-directives.ts — turns `:::tip`, `:term[...]`, etc. into custom elements.
 *
 * How Markdown becomes React here (the "unified" pipeline):
 *   Markdown text ──remark──▶ mdast (Markdown syntax tree)
 *                 ──remark plugins (this file)──▶ modified mdast
 *                 ──remark-rehype──▶ hast (HTML syntax tree)
 *                 ──react-markdown──▶ React elements (custom tags → our components)
 *
 * `remark-directive` only PARSES the `:::name{attr="x"}` syntax. This plugin decides
 * what each directive becomes by setting `data.hName` (tag name) and
 * `data.hProperties` (props).
 *
 * Teaches: working with syntax trees, and the "visitor" pattern (`visit`).
 */
import type { Root, RootContent } from 'mdast'
import type { ContainerDirective, LeafDirective, TextDirective } from 'mdast-util-directive'
import { visit } from 'unist-util-visit'

type Directive = ContainerDirective | LeafDirective | TextDirective

/** Which directive names are allowed, per kind. Anything else is shown as plain text. */
export const CONTAINER_DIRECTIVES = [
  'tip',
  'note',
  'warning',
  'danger',
  'revoshop',
  'fastapi',
  'bahasa',
  'hints',
  'quiz',
  'exercise',
  'linkedin',
  'placement',
  'sandpack',
  'problem',
] as const
export const LEAF_DIRECTIVES = ['part', 'ai-review'] as const
export const TEXT_DIRECTIVES = ['term'] as const

const allowed = {
  containerDirective: new Set<string>(CONTAINER_DIRECTIVES),
  leafDirective: new Set<string>(LEAF_DIRECTIVES),
  textDirective: new Set<string>(TEXT_DIRECTIVES),
}

const CALLOUTS = new Set(['tip', 'note', 'warning', 'danger', 'revoshop', 'fastapi', 'bahasa'])

export function remarkHandbookDirectives() {
  return (tree: Root) => {
    visit(tree, (node, index, parent) => {
      if (
        node.type !== 'containerDirective' &&
        node.type !== 'leafDirective' &&
        node.type !== 'textDirective'
      ) {
        return
      }
      const directive = node as Directive

      // Unknown directive? It was probably normal text like "Note:Hello".
      // Put the original text back instead of silently dropping it.
      if (!allowed[directive.type].has(directive.name)) {
        if (parent && typeof index === 'number') {
          parent.children.splice(index, 1, ...restoreAsText(directive))
        }
        return
      }

      const attributes = { ...(directive.attributes ?? {}) }
      const data = (directive.data ??= {})

      if (directive.type === 'textDirective') {
        // :term[Middleware]{bahasa="perantara"}
        data.hName = 'term'
        data.hProperties = attributes
        return
      }

      if (directive.type === 'leafDirective' && directive.name === 'ai-review') {
        // ::ai-review{task="explain"}
        data.hName = 'ai-review'
        data.hProperties = attributes
        return
      }

      if (directive.type === 'leafDirective') {
        // ::part[Learn the Concept]{n="1"}
        data.hName = 'part-divider'
        data.hProperties = { ...attributes, label: plainLabel(directive) }
        directive.children = []
        return
      }

      // Container directives. The optional [label] becomes a `title` prop.
      const label = extractContainerLabel(directive)
      if (label) attributes.title ??= label

      if (CALLOUTS.has(directive.name)) {
        data.hName = 'callout'
        data.hProperties = { ...attributes, variant: directive.name }
        return
      }

      if (directive.name === 'hints') {
        markListItems(directive, 'hint-item')
      }

      if (directive.name === 'quiz') {
        // First paragraph = question, everything after = answer.
        const [question, ...answer] = directive.children
        if (question) {
          directive.children = [
            wrap('quiz-question', [question]),
            wrap('quiz-answer', answer as RootContent[]),
          ] as ContainerDirective['children']
        }
      }

      if (directive.name === 'sandpack') {
        // Collect ```lang filename code blocks into a files object for the editor.
        const files: Record<string, string> = {}
        for (const child of directive.children) {
          if (child.type === 'code' && child.meta) files[child.meta.trim()] = child.value
        }
        attributes.files = JSON.stringify(files)
        directive.children = []
      }

      data.hName = directive.name // hints, quiz, exercise, linkedin, placement, sandpack, problem
      data.hProperties = attributes
    })
  }
}

// ── helpers ──────────────────────────────────────────────────────────────────

function plainLabel(node: { children?: unknown[] }): string {
  return (node.children ?? [])
    .map((child) => (child as { value?: string }).value ?? plainLabel(child as { children?: unknown[] }))
    .join('')
}

/** remark-directive stores `:::tip[My title]` as a first paragraph flagged `directiveLabel`. */
function extractContainerLabel(directive: ContainerDirective): string | undefined {
  const first = directive.children[0]
  if (first?.type === 'paragraph' && first.data?.directiveLabel) {
    directive.children.shift()
    return plainLabel(first)
  }
  return undefined
}

function markListItems(directive: ContainerDirective, hName: string) {
  for (const child of directive.children) {
    if (child.type !== 'list') continue
    child.data = { ...child.data, hName: 'hint-list' }
    for (const item of child.children) {
      item.data = { ...item.data, hName }
    }
  }
}

function wrap(hName: string, children: RootContent[]) {
  return { type: 'blockquote', data: { hName }, children } as unknown as RootContent
}

function restoreAsText(directive: Directive): RootContent[] {
  const colons = directive.type === 'textDirective' ? ':' : directive.type === 'leafDirective' ? '::' : ':::'
  const prefix = { type: 'text', value: `${colons}${directive.name}` } as RootContent
  return [prefix, ...(directive.children as RootContent[])]
}

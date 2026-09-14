/**
 * MarkdownRenderer.tsx — turns a lesson's Markdown into React components.
 *
 * Teaches:
 * - Composition: react-markdown does the parsing; we plug in remark/rehype plugins
 *   and choose which React component renders each element.
 * - Overriding built-in elements (a, pre, code, table) and adding custom ones
 *   (callout, term, quiz…) created by remark-directives.ts.
 */
import { lazy, memo, Suspense, type ComponentProps, type ReactNode } from 'react'
import ReactMarkdown, { type Components } from 'react-markdown'
import { Link } from 'react-router'
import rehypeSlug from 'rehype-slug'
import remarkDirective from 'remark-directive'
import remarkGfm from 'remark-gfm'
import { remarkHandbookDirectives } from '../../content/remark-directives'
import { useLocale } from '../../hooks/useLocale'
import { AiReviewSlot } from './AiReviewSlot'
import { Callout } from './Callout'
import { CodeBlock } from './CodeBlock'
import { ExerciseCard } from './ExerciseCard'
import { HintItem, HintList, Hints } from './Hints'
import { LinkedInCard } from './LinkedInCard'
import { Mermaid } from './Mermaid'
import { PartDivider } from './PartDivider'
import { PlacementCheck } from './PlacementCheck'
import { ProblemCard } from './ProblemCard'
import { Quiz, QuizAnswer, QuizQuestion } from './Quiz'
import { Term } from './Term'

type WithChildren = { children?: ReactNode }

// Loaded only when a lesson actually contains an in-browser editor.
const SandpackBlock = lazy(() => import('./SandpackBlock'))

/** Custom element names produced by our remark plugin → their components. */
function SandpackLoader(props: ComponentProps<typeof SandpackBlock>) {
  const { t } = useLocale()
  return (
    <Suspense fallback={<p className="text-sm text-slate-400">{t('sandpack.loading')}</p>}>
      <SandpackBlock {...props} />
    </Suspense>
  )
}

const customComponents = {
  callout: Callout,
  term: Term,
  hints: Hints,
  'hint-list': HintList,
  'hint-item': HintItem,
  quiz: Quiz,
  'quiz-question': QuizQuestion,
  'quiz-answer': QuizAnswer,
  'part-divider': PartDivider,
  exercise: ExerciseCard,
  problem: ProblemCard,
  linkedin: LinkedInCard,
  placement: PlacementCheck,
  'ai-review': AiReviewSlot,
  sandpack: SandpackLoader,
}

const components = {
  ...customComponents,

  // Internal links use the router (no full page reload); external links open a new tab.
  a({ href = '', children, node: _node, ...rest }: ComponentProps<'a'> & { node?: unknown }) {
    if (href.startsWith('/')) {
      return <Link to={href}>{children}</Link>
    }
    const external = /^https?:\/\//.test(href)
    return (
      <a href={href} {...rest} {...(external ? { target: '_blank', rel: 'noreferrer' } : {})}>
        {children}
      </a>
    )
  },

  // CodeBlock renders its own wrapper, so <pre> just passes children through.
  pre({ children }: WithChildren) {
    return <>{children}</>
  },

  code({ className, children }: ComponentProps<'code'>) {
    const text = String(children ?? '')
    const language = /language-([\w-]+)/.exec(className ?? '')?.[1]
    const isBlock = Boolean(language) || text.includes('\n')

    if (!isBlock) return <code className={className}>{children}</code>
    if (language === 'mermaid') return <Mermaid code={text.trimEnd()} />
    return <CodeBlock code={text.replace(/\n$/, '')} language={language ?? 'text'} />
  },

  // Wide tables scroll sideways instead of breaking the layout on phones.
  table({ children }: WithChildren) {
    return (
      <div className="overflow-x-auto">
        <table>{children}</table>
      </div>
    )
  },
} as Components

const remarkPlugins = [remarkGfm, remarkDirective, remarkHandbookDirectives]
const rehypePlugins = [rehypeSlug]

export const MarkdownRenderer = memo(function MarkdownRenderer({ markdown }: { markdown: string }) {
  return (
    <div className="prose prose-slate max-w-none dark:prose-invert prose-headings:scroll-mt-20 prose-a:text-indigo-600 prose-code:before:content-none prose-code:after:content-none dark:prose-a:text-indigo-400 [&_:not(pre)>code]:rounded [&_:not(pre)>code]:bg-slate-100 [&_:not(pre)>code]:px-1.5 [&_:not(pre)>code]:py-0.5 [&_:not(pre)>code]:font-normal dark:[&_:not(pre)>code]:bg-slate-800">
      <ReactMarkdown
        remarkPlugins={remarkPlugins}
        rehypePlugins={rehypePlugins}
        components={components}
      >
        {markdown}
      </ReactMarkdown>
    </div>
  )
})

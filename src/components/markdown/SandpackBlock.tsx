/**
 * SandpackBlock.tsx — an in-browser code editor that runs JS/TS/React (and tests).
 *
 * Markdown:
 *   :::sandpack{template="test-ts" title="Sum an array"}
 *   ```ts sum.ts
 *   export function sum(values: number[]) { return 0 }
 *   ```
 *   ```ts sum.test.ts
 *   import { sum } from './sum'
 *   test('adds numbers', () => expect(sum([1, 2])).toBe(3))
 *   ```
 *   :::
 *
 * This file is loaded lazily (see MarkdownRenderer), because Sandpack is big and
 * most lessons don't use it. It needs an internet connection: the code runs
 * inside CodeSandbox's bundler iframe.
 */
import {
  SandpackCodeEditor,
  SandpackConsole,
  SandpackLayout,
  SandpackPreview,
  SandpackProvider,
  SandpackTests,
} from '@codesandbox/sandpack-react'
import { useLocale } from '../../hooks/useLocale'
import { useTheme } from '../../hooks/useTheme'

const TEMPLATES = ['vanilla-ts', 'react-ts', 'test-ts', 'vanilla', 'react'] as const
type Template = (typeof TEMPLATES)[number]

type SandpackBlockProps = {
  template?: string
  title?: string
  files?: string
  console?: string
}

function parseFiles(json: string | undefined): Record<string, string> {
  try {
    const parsed = JSON.parse(json ?? '{}') as Record<string, string>
    // Sandpack expects absolute paths like "/App.tsx".
    return Object.fromEntries(
      Object.entries(parsed).map(([name, code]) => [
        name.startsWith('/') ? name : `/${name}`,
        code,
      ]),
    )
  } catch {
    return {}
  }
}

export default function SandpackBlock({
  template,
  title,
  files,
  console: showConsole,
}: SandpackBlockProps) {
  const { resolved } = useTheme()
  const { t } = useLocale()
  const fileMap = parseFiles(files)
  const names = Object.keys(fileMap)
  const hasTests = names.some((name) => /\.test\.[jt]sx?$/.test(name))
  const requested: Template = TEMPLATES.includes(template as Template)
    ? (template as Template)
    : 'vanilla-ts'
  // The "test-ts" template ships its own sample test, which would run next to ours.
  // Sandpack's test runner works with any template, so use the plain TS one instead.
  const chosenTemplate: Template = requested === 'test-ts' ? 'vanilla-ts' : requested
  const activeFile = names.find((name) => !/\.test\./.test(name)) ?? names[0]

  return (
    <section className="not-prose my-8">
      <div className="mb-2 flex items-center justify-between text-sm">
        <p className="font-semibold text-slate-900 dark:text-white">
          🧸 {title ?? t('sandpack.defaultTitle')}
        </p>
        <span className="text-xs text-slate-500">{t('sandpack.note')}</span>
      </div>
      <SandpackProvider
        template={chosenTemplate}
        files={fileMap}
        theme={resolved}
        options={{ activeFile, visibleFiles: names.length ? names : undefined }}
      >
        <SandpackLayout className="!rounded-xl">
          <SandpackCodeEditor showTabs showLineNumbers style={{ height: 380 }} />
          {hasTests ? (
            <SandpackTests
              style={{ height: 380 }}
              showVerboseButton={false}
              showWatchButton={false}
            />
          ) : (
            <SandpackPreview style={{ height: 380 }} showOpenInCodeSandbox={false} />
          )}
        </SandpackLayout>
        {showConsole === 'true' && !hasTests && (
          <SandpackConsole className="mt-2 rounded-xl" style={{ height: 160 }} />
        )}
      </SandpackProvider>
    </section>
  )
}

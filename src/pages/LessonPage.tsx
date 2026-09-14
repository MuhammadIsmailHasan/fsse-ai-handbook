/**
 * LessonPage.tsx — renders any lesson (module, track, project or guide).
 *
 * Teaches:
 * - The URL IS the lesson id: "/modules/m1/w0/01-intro" → "modules/m1/w0/01-intro".
 *   One page component serves every lesson route.
 * - React 19 `use()` + <Suspense>: "wait for this Promise" without useEffect;
 *   Suspense shows a fallback while it loads.
 * - Splitting a page into small components with clear jobs.
 */
import { Suspense, use, useCallback, useState } from 'react'
import { Link, useLocation } from 'react-router'
import { DoneButton } from '../components/lesson/DoneButton'
import { NotesPanel } from '../components/lesson/NotesPanel'
import { TableOfContents } from '../components/lesson/TableOfContents'
import { MarkdownRenderer } from '../components/markdown/MarkdownRenderer'
import { RoleBadges } from '../components/ui/RoleBadges'
import { getLessonBodyPromise, type ContentApi } from '../content'
import { useContent } from '../hooks/useContent'
import { useLocale } from '../hooks/useLocale'
import type { MessageKey, MessageValues } from '../i18n/messages'
import { collectHeadings, type TocHeading } from '../lib/headings'
import type { LessonMeta } from '../types/content'
import { NotFoundPage } from './NotFoundPage'

type Translate = (key: MessageKey, values?: MessageValues) => string

export function LessonPage() {
  const { pathname } = useLocation()
  const { getLesson } = useContent()
  const { t } = useLocale()
  const lesson = getLesson(decodeURIComponent(pathname).replace(/^\/+|\/+$/g, ''))

  if (!lesson) return <NotFoundPage />

  return (
    // `key` resets the page state when navigating between lessons or switching language.
    <article key={`${lesson.id}:${lesson.language}`} className="mx-auto max-w-6xl">
      <Suspense
        fallback={
          <div className="max-w-3xl">
            <LessonHeader lesson={lesson} />
            <p className="text-slate-400">{t('lesson.loading')}</p>
          </div>
        }
      >
        <LessonBody lesson={lesson} />
      </Suspense>
    </article>
  )
}

function LessonBody({ lesson }: { lesson: LessonMeta }) {
  const markdown = use(getLessonBodyPromise(lesson))
  const [headings, setHeadings] = useState<TocHeading[]>([])

  // A "ref callback" runs when the element is attached to the page —
  // by then the Markdown headings exist and we can read them.
  const contentRef = useCallback((element: HTMLDivElement | null) => {
    if (element) setHeadings(collectHeadings(element))
  }, [])

  return (
    <div className="xl:grid xl:grid-cols-[minmax(0,48rem)_14rem] xl:gap-12">
      <div className="min-w-0">
        <LessonHeader lesson={lesson} />
        <div ref={contentRef}>
          <MarkdownRenderer markdown={markdown} />
        </div>
        <div className="mt-12 flex justify-center">
          <DoneButton lessonId={lesson.id} />
        </div>
        <NotesPanel lessonId={lesson.id} />
        <LessonNav lesson={lesson} />
      </div>
      <aside className="hidden xl:block">
        <div className="sticky top-20 max-h-[calc(100dvh-6rem)] overflow-y-auto">
          <TableOfContents headings={headings} />
        </div>
      </aside>
    </div>
  )
}

function breadcrumb(lesson: LessonMeta, content: ContentApi, t: Translate): string {
  const { getModule, getTrack, getProject } = content
  switch (lesson.collection) {
    case 'modules': {
      const module = getModule(lesson.group)
      const week = module?.weeks.find((w) => w.id === lesson.section)
      return [
        module && t('lesson.module', { number: module.number, title: module.title }),
        week?.title,
      ]
        .filter(Boolean)
        .join('  ›  ')
    }
    case 'tracks': {
      const track = getTrack(lesson.group)
      const stage = track?.stages.find((s) => s.id === lesson.section)
      return [track?.title, stage?.title].filter(Boolean).join('  ›  ')
    }
    case 'projects':
      return getProject(lesson.group)?.title ?? t('lesson.project')
    case 'guides':
      return t('lesson.guide')
  }
}

function LessonHeader({ lesson }: { lesson: LessonMeta }) {
  const content = useContent()
  const { t, locale, formatNumber } = useLocale()

  return (
    <header className="mb-10 border-b border-slate-200 pb-8 dark:border-slate-800">
      <p className="mb-2 text-sm font-medium text-indigo-600 dark:text-indigo-400">
        {breadcrumb(lesson, content, t)}
      </p>
      <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl dark:text-white">
        {lesson.title}
      </h1>
      <p className="mt-3 text-lg text-slate-600 dark:text-slate-400">{lesson.summary}</p>

      {lesson.language !== locale && (
        <p
          className="mt-4 rounded-lg border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900 dark:border-amber-500/40 dark:bg-amber-500/10 dark:text-amber-200"
          role="note"
        >
          <strong>🇬🇧 {t('lesson.notTranslated')}</strong> — {t('lesson.notTranslatedDetail')}
        </p>
      )}

      <div className="mt-5 flex flex-wrap items-center gap-2 text-xs">
        {lesson.source === 'core' ? (
          <Chip>{t('lesson.sourceRef', { ref: lesson.sourceRef ?? '' })}</Chip>
        ) : (
          <Chip>{t('lesson.bonus')}</Chip>
        )}
        {lesson.split && <Chip>{t('lesson.split')}</Chip>}
        <Chip>
          {t('lesson.studyHours', {
            hours: formatNumber(Math.round((lesson.durationMinutes / 60) * 10) / 10),
          })}
        </Chip>
        <Chip>{t('lesson.readMinutes', { minutes: lesson.readingMinutes })}</Chip>
        {lesson.lastReviewed && <Chip>{t('lesson.reviewed', { date: lesson.lastReviewed })}</Chip>}
        {lesson.awsCost && <Chip>{t(AWS_COST[lesson.awsCost])}</Chip>}
      </div>

      <div className="mt-3">
        <RoleBadges roles={lesson.roles} />
      </div>

      <div className="mt-5">
        <DoneButton lessonId={lesson.id} size="sm" />
      </div>
    </header>
  )
}

const AWS_COST = {
  free: 'lesson.awsFree',
  small: 'lesson.awsSmall',
  concept: 'lesson.awsConcept',
} as const

function Chip({ children }: { children: React.ReactNode }) {
  return (
    <span className="rounded-md bg-slate-100 px-2 py-1 font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
      {children}
    </span>
  )
}

function LessonNav({ lesson }: { lesson: LessonMeta }) {
  const { getNeighbors } = useContent()
  const { t } = useLocale()
  const { previous, next } = getNeighbors(lesson)

  return (
    <nav className="mt-16 grid gap-3 border-t border-slate-200 pt-8 sm:grid-cols-2 dark:border-slate-800">
      {previous ? (
        <NavCard
          to={previous.url}
          direction="previous"
          label={t('lesson.previous')}
          title={previous.title}
        />
      ) : (
        <span />
      )}
      {next && (
        <NavCard
          to={next.url}
          direction="next"
          label={t('lesson.next')}
          title={next.title}
          alignRight
        />
      )}
    </nav>
  )
}

function NavCard(props: {
  to: string
  direction: 'previous' | 'next'
  label: string
  title: string
  alignRight?: boolean
}) {
  return (
    <Link
      to={props.to}
      className={`rounded-xl border border-slate-200 p-4 hover:border-indigo-400 dark:border-slate-800 dark:hover:border-indigo-500 ${props.alignRight ? 'text-right sm:col-start-2' : ''}`}
    >
      <span className="text-xs text-slate-500">
        {props.direction === 'previous' ? '← ' : ''}
        {props.label}
        {props.direction === 'next' ? ' →' : ''}
      </span>
      <span className="mt-1 block font-medium text-slate-900 dark:text-white">{props.title}</span>
    </Link>
  )
}

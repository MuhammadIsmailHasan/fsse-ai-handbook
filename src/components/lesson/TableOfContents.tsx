/**
 * TableOfContents.tsx — "On this page" links that highlight the section you're reading.
 *
 * Teaches:
 * - IntersectionObserver: the browser tells us when headings enter the viewport,
 *   which is much cheaper than listening to every scroll event.
 * - Setting state from an observer CALLBACK (async) inside an effect is fine;
 *   setting it synchronously in the effect body would cause extra renders.
 */
import { useEffect, useState } from 'react'
import { useLocale } from '../../hooks/useLocale'
import type { TocHeading } from '../../lib/headings'

export function TableOfContents({ headings }: { headings: TocHeading[] }) {
  const [activeId, setActiveId] = useState<string | null>(null)
  const { t } = useLocale()

  useEffect(() => {
    const elements = headings
      .map((heading) => document.getElementById(heading.id))
      .filter((element): element is HTMLElement => element !== null)

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((entry) => entry.isIntersecting)
        if (visible[0]) setActiveId(visible[0].target.id)
      },
      // Treat a heading as "current" when it's in the top part of the screen.
      { rootMargin: '-64px 0px -70% 0px' },
    )

    elements.forEach((element) => observer.observe(element))
    return () => observer.disconnect()
  }, [headings])

  if (headings.length === 0) return null

  return (
    <nav aria-label={t('lesson.onThisPage')} className="text-sm">
      <p className="mb-3 text-xs font-semibold tracking-wider text-slate-400 uppercase">
        {t('lesson.onThisPage')}
      </p>
      <ul className="space-y-1.5 border-l border-slate-200 dark:border-slate-800">
        {headings.map((heading) => (
          <li key={heading.id}>
            <a
              href={`#${heading.id}`}
              className={`-ml-px block border-l py-0.5 leading-snug ${heading.level === 3 ? 'pl-6' : 'pl-3'} ${
                activeId === heading.id
                  ? 'border-indigo-500 font-medium text-indigo-700 dark:text-indigo-300'
                  : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
              }`}
            >
              {heading.text}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  )
}

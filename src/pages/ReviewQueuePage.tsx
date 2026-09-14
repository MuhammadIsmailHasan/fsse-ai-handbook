/**
 * ReviewQueuePage.tsx — DSA problems due for spaced review.
 *
 * Teaches: computing lists from state with pure helpers (dueItems/upcomingItems),
 * so the page stays small and the logic stays tested.
 */
import { Link } from 'react-router'
import { PageHeader } from '../components/ui/PageHeader'
import { useLocale } from '../hooks/useLocale'
import { useStudy } from '../hooks/useStudy'
import { dueItems, INTERVALS_DAYS, upcomingItems, type ReviewItem } from '../lib/spaced-repetition'

export function ReviewQueuePage() {
  const { reviewQueue, reviewProblem } = useStudy()
  const today = new Date()
  const due = dueItems(reviewQueue, today)
  const upcoming = upcomingItems(reviewQueue, today)
  const mastered = Object.values(reviewQueue).filter((item) => item.mastered)
  const { t } = useLocale()

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader
        eyebrow={t('review.eyebrow')}
        title={t('review.title')}
        description={t('review.description', { intervals: INTERVALS_DAYS.join(' → ') })}
      />

      <section className="mb-10">
        <h2 className="mb-3 font-semibold text-slate-900 dark:text-white">
          {t('review.dueToday', { count: due.length })}
        </h2>
        {due.length === 0 ? (
          <p className="rounded-xl border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500 dark:border-slate-700">
            {t('review.nothingDueBefore')}{' '}
            <Link to="/tracks/dsa" className="text-indigo-600 hover:underline dark:text-indigo-400">
              {t('review.dsaTrack')}
            </Link>{' '}
            {t('review.nothingDueAfter')}
          </p>
        ) : (
          <ul className="space-y-2">
            {due.map((item) => (
              <li
                key={item.id}
                className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 p-4 dark:border-slate-800"
              >
                <ItemInfo item={item} />
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => reviewProblem(item.id, 'forgot')}
                    className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800"
                  >
                    {t('review.forgot')}
                  </button>
                  <button
                    type="button"
                    onClick={() => reviewProblem(item.id, 'remembered')}
                    className="rounded-lg bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-700"
                  >
                    {t('review.remembered')}
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mb-10">
        <h2 className="mb-3 font-semibold text-slate-900 dark:text-white">
          {t('review.upcoming', { count: upcoming.length })}
        </h2>
        <ul className="divide-y divide-slate-100 dark:divide-slate-800">
          {upcoming.map((item) => (
            <li key={item.id} className="flex items-center justify-between gap-3 py-2">
              <ItemInfo item={item} />
              <span className="text-sm text-slate-500 tabular-nums">{item.nextDue}</span>
            </li>
          ))}
        </ul>
      </section>

      {mastered.length > 0 && (
        <p className="text-sm text-slate-500">
          {t('review.mastered', { titles: mastered.map((item) => item.title).join(', ') })}
        </p>
      )}
    </div>
  )
}

function ItemInfo({ item }: { item: ReviewItem }) {
  const { t } = useLocale()

  return (
    <div className="min-w-0">
      <Link
        to={item.lessonUrl}
        className="font-medium text-slate-900 hover:text-indigo-700 dark:text-white dark:hover:text-indigo-300"
      >
        {item.title}
      </Link>
      <p className="text-xs text-slate-500">
        {item.difficulty ? `${t(`problem.${item.difficulty}`)} · ` : ''}
        {t('review.reviews', { count: item.reviews })}
      </p>
    </div>
  )
}

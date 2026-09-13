/**
 * ReviewQueuePage.tsx — DSA problems due for spaced review.
 *
 * Teaches: computing lists from state with pure helpers (dueItems/upcomingItems),
 * so the page stays small and the logic stays tested.
 */
import { Link } from 'react-router'
import { PageHeader } from '../components/ui/PageHeader'
import { useStudy } from '../hooks/useStudy'
import { dueItems, INTERVALS_DAYS, upcomingItems, type ReviewItem } from '../lib/spaced-repetition'

export function ReviewQueuePage() {
  const { reviewQueue, reviewProblem } = useStudy()
  const today = new Date()
  const due = dueItems(reviewQueue, today)
  const upcoming = upcomingItems(reviewQueue, today)
  const mastered = Object.values(reviewQueue).filter((item) => item.mastered)

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader
        eyebrow="DSA for Interviews"
        title="🔁 Review Queue"
        description={`Solve each problem again from scratch — no peeking. Remembered it? The next review moves further away (${INTERVALS_DAYS.join(' → ')} days). Forgot? Back to 1 day.`}
      />

      <section className="mb-10">
        <h2 className="mb-3 font-semibold text-slate-900 dark:text-white">
          Due today ({due.length})
        </h2>
        {due.length === 0 ? (
          <p className="rounded-xl border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500 dark:border-slate-700">
            Nothing due. 🎉 Solve new problems in the{' '}
            <Link to="/tracks/dsa" className="text-indigo-600 hover:underline dark:text-indigo-400">
              DSA track
            </Link>{' '}
            to fill your queue.
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
                    😵 Forgot
                  </button>
                  <button
                    type="button"
                    onClick={() => reviewProblem(item.id, 'remembered')}
                    className="rounded-lg bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-700"
                  >
                    💪 Remembered
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mb-10">
        <h2 className="mb-3 font-semibold text-slate-900 dark:text-white">
          Upcoming ({upcoming.length})
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
          🏆 Mastered: {mastered.map((item) => item.title).join(', ')}
        </p>
      )}
    </div>
  )
}

function ItemInfo({ item }: { item: ReviewItem }) {
  return (
    <div className="min-w-0">
      <Link
        to={item.lessonUrl}
        className="font-medium text-slate-900 hover:text-indigo-700 dark:text-white dark:hover:text-indigo-300"
      >
        {item.title}
      </Link>
      <p className="text-xs text-slate-500">
        {item.difficulty ? `${item.difficulty} · ` : ''}reviews: {item.reviews}
      </p>
    </div>
  )
}

/**
 * SchedulePage.tsx — "Study Plan": plan today from the time you really have,
 * log what you studied, and see the week.
 *
 * Teaches:
 * - Splitting a page into small components that each own one job.
 * - Deriving everything (today's plan, weekly totals) from a few stored values:
 *   the goal, the time log and completed lessons. Nothing derived is stored.
 */
import { useState } from 'react'
import { Link } from 'react-router'
import { PageHeader } from '../components/ui/PageHeader'
import { ProgressBar } from '../components/ui/ProgressBar'
import { orderedStream, pickForBudget } from '../content/planning'
import { useContent } from '../hooks/useContent'
import { useLocale } from '../hooks/useLocale'
import { useNow } from '../hooks/useNow'
import { usePersistentState } from '../hooks/usePersistentState'
import { useStudy } from '../hooks/useStudy'
import type { MessageKey } from '../i18n/messages'
import { dueItems } from '../lib/spaced-repetition'
import { STORAGE_KEYS } from '../lib/storage'
import {
  dateKey,
  planDay,
  recentAverage,
  summarizeWeek,
  weekDates,
  weeklyBudget,
  type Stream,
} from '../lib/study-time'
import type { LessonMeta } from '../types/content'

const STREAM_TITLE: Record<Stream, MessageKey> = {
  module: 'schedule.streamModule',
  dsa: 'schedule.streamDsa',
  architecture: 'schedule.streamArchitecture',
  project: 'schedule.streamProject',
}

const TIME_CHOICES = [30, 60, 120, 180, 240, 300, 360]

export function SchedulePage() {
  const { reviewQueue } = useStudy()
  const { t } = useLocale()
  const due = dueItems(reviewQueue, new Date()).length

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <PageHeader
        eyebrow={t('schedule.eyebrow')}
        title={t('schedule.title')}
        description={t('schedule.description')}
      />

      {due > 0 && (
        <Link
          to="/tracks/dsa/review"
          className="block rounded-xl border border-amber-300 bg-amber-50 px-5 py-3 text-sm font-medium text-amber-900 dark:border-amber-500/40 dark:bg-amber-500/10 dark:text-amber-200"
        >
          {due === 1 ? t('schedule.dueOne') : t('schedule.dueMany', { count: due })}
        </Link>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <TodayCard />
        <TimeLogCard />
      </div>
      <WeekCard />
      <WeekLessons />
    </div>
  )
}

/** Hook: the lessons of one stream, in the recommended order. */
function useStreamLessons() {
  const { allLessons, course } = useContent()
  return (stream: Stream) => orderedStream(course.studyPath[stream], allLessons)
}

// ── Today: "how much time do you have?" → a plan that fits ──────────────────

function TodayCard() {
  const { completed, targetRole, studyGoal } = useStudy()
  const { t, formatDuration } = useLocale()
  const streamLessons = useStreamLessons()
  const today = new Date()
  const todayKey = dateKey(today)

  // Remember today's answer; a new day starts again from the target.
  const [choice, setChoice] = usePersistentState<{ date: string; minutes: number } | null>(
    STORAGE_KEYS.todayPlan,
    null,
  )
  const available = choice?.date === todayKey ? choice.minutes : studyGoal.targetMinutes
  const choices = [...new Set([...TIME_CHOICES, studyGoal.targetMinutes])].sort((a, b) => a - b)

  return (
    <section className="rounded-xl border border-slate-200 p-5 dark:border-slate-800">
      <h2 className="font-semibold text-slate-900 dark:text-white">{t('today.heading')}</h2>
      <fieldset className="mt-3">
        <legend className="text-sm text-slate-600 dark:text-slate-400">
          {t('today.question')}
        </legend>
        <div className="mt-2 flex flex-wrap gap-1.5">
          {choices.map((minutes) => (
            <label
              key={minutes}
              className="cursor-pointer rounded-full border border-slate-300 px-3 py-1 text-sm has-checked:border-indigo-600 has-checked:bg-indigo-600 has-checked:text-white dark:border-slate-700"
              title={minutes === studyGoal.targetMinutes ? t('today.targetTitle') : undefined}
            >
              <input
                type="radio"
                name="today-time"
                className="sr-only"
                checked={available === minutes}
                onChange={() => setChoice({ date: todayKey, minutes })}
              />
              {minutes === studyGoal.targetMinutes ? '🎯 ' : ''}
              {formatDuration(minutes)}
            </label>
          ))}
        </div>
      </fieldset>

      <ol className="mt-5 space-y-4">
        {planDay(available, today).map((block) => {
          const lessons = pickForBudget(
            streamLessons(block.stream),
            completed,
            targetRole,
            block.minutes,
          )
          const first = lessons[0]
          return (
            <li key={block.stream}>
              <div className="flex items-baseline justify-between gap-2">
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                  {t(STREAM_TITLE[block.stream])}
                </h3>
                <span className="text-sm font-medium text-indigo-700 tabular-nums dark:text-indigo-300">
                  {formatDuration(block.minutes)}
                </span>
              </div>
              {!first ? (
                <p className="mt-1 text-xs text-slate-500">{t('today.streamDone')}</p>
              ) : (
                <ul className="mt-1 space-y-1">
                  {lessons.slice(0, 3).map((lesson) => (
                    <li key={lesson.id}>
                      <Link
                        to={lesson.url}
                        className="block rounded-md px-2 py-1 text-sm hover:bg-slate-50 dark:hover:bg-slate-900"
                      >
                        <span className="text-slate-900 dark:text-white">{lesson.title}</span>
                        {lesson === first && lesson.durationMinutes > block.minutes && (
                          <span className="block text-xs text-slate-500">
                            {t('today.partial', {
                              time: formatDuration(block.minutes),
                              total: formatDuration(lesson.durationMinutes),
                            })}
                          </span>
                        )}
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </li>
          )
        })}
      </ol>
    </section>
  )
}

// ── Time log: timer + quick buttons ─────────────────────────────────────────

const clock = (totalSeconds: number) => {
  const h = Math.floor(totalSeconds / 3600)
  const m = Math.floor((totalSeconds % 3600) / 60)
  const s = totalSeconds % 60
  const pad = (n: number) => String(n).padStart(2, '0')
  return h > 0 ? `${h}:${pad(m)}:${pad(s)}` : `${m}:${pad(s)}`
}

function TimeLogCard() {
  const { studyGoal, studyLog, addStudyMinutes, timerStartedAt, startTimer, stopTimer, completed } =
    useStudy()
  const { allLessons } = useContent()
  const { t, formatDuration } = useLocale()
  const now = useNow(1000, timerStartedAt !== null)
  const [message, setMessage] = useState<string | null>(null)

  const todayKey = dateKey(new Date())
  const minutes = studyLog[todayKey] ?? 0
  const { targetMinutes, minimumMinutes } = studyGoal
  const lessonsDoneMinutes = allLessons
    .filter(
      (lesson) => completed[lesson.id] && dateKey(new Date(completed[lesson.id]!)) === todayKey,
    )
    .reduce((sum, lesson) => sum + lesson.durationMinutes, 0)

  const runningSeconds = timerStartedAt
    ? Math.max(0, Math.floor((now.getTime() - Date.parse(timerStartedAt)) / 1000))
    : 0

  const buttonClass =
    'rounded-lg border border-slate-300 px-2.5 py-1 text-sm font-medium tabular-nums hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800'

  return (
    <section className="rounded-xl border border-slate-200 p-5 dark:border-slate-800">
      <h2 className="font-semibold text-slate-900 dark:text-white">{t('log.heading')}</h2>
      <p className="mt-3 text-2xl font-bold text-slate-900 tabular-nums dark:text-white">
        {t('log.progress', {
          done: formatDuration(minutes),
          target: formatDuration(targetMinutes),
        })}
      </p>
      <div className="mt-2">
        <ProgressBar
          percent={Math.min(100, Math.round((minutes / targetMinutes) * 100))}
          label={t('log.progressLabel')}
        />
      </div>
      <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
        {minutes >= targetMinutes
          ? t('log.targetMet')
          : minutes >= minimumMinutes
            ? t('log.minimumMet', { minimum: formatDuration(minimumMinutes) })
            : t('log.minimumLeft', {
                left: formatDuration(minimumMinutes - minutes),
                minimum: formatDuration(minimumMinutes),
              })}
      </p>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        {timerStartedAt ? (
          <button
            type="button"
            onClick={() => {
              const added = stopTimer()
              setMessage(t('log.stopped', { time: formatDuration(added) }))
            }}
            className="rounded-lg bg-rose-600 px-3 py-1.5 text-sm font-medium text-white tabular-nums hover:bg-rose-700"
          >
            {t('log.stop', { time: clock(runningSeconds) })}
          </button>
        ) : (
          <button
            type="button"
            onClick={() => {
              startTimer()
              setMessage(null)
            }}
            className="rounded-lg bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700"
          >
            {t('log.start')}
          </button>
        )}
        {[15, 30, 60].map((delta) => (
          <button
            key={delta}
            type="button"
            className={buttonClass}
            onClick={() => addStudyMinutes(todayKey, delta)}
          >
            {t('log.add', { time: formatDuration(delta) })}
          </button>
        ))}
        <button
          type="button"
          className={buttonClass}
          disabled={minutes === 0}
          aria-label={t('log.removeLabel', { time: formatDuration(15) })}
          onClick={() => addStudyMinutes(todayKey, -15)}
        >
          {t('log.remove', { time: formatDuration(15) })}
        </button>
      </div>

      <p className="mt-3 text-xs text-slate-500" role="status">
        {message ?? t('log.help')}
      </p>
      {lessonsDoneMinutes > 0 && (
        <p className="mt-1 text-xs text-slate-500">
          {t('log.lessonsDoneToday', { time: formatDuration(lessonsDoneMinutes) })}
        </p>
      )}
    </section>
  )
}

// ── Week: bars per day, totals, and an honest average ───────────────────────

function WeekCard() {
  const { studyGoal, studyLog } = useStudy()
  const { t, formatDuration, intlLocale } = useLocale()
  const today = new Date()
  const week = summarizeWeek(studyLog, studyGoal, today)
  const average = recentAverage(studyLog, studyGoal, today)
  const weekdayName = new Intl.DateTimeFormat(intlLocale, { weekday: 'short' })
  const dates = weekDates(today)

  return (
    <section className="rounded-xl border border-slate-200 p-5 dark:border-slate-800">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="font-semibold text-slate-900 dark:text-white">{t('week.heading')}</h2>
        <span className="text-sm font-medium text-slate-700 tabular-nums dark:text-slate-300">
          {t('week.total', {
            done: formatDuration(week.totalMinutes),
            target: formatDuration(week.targetMinutes),
          })}
        </span>
      </div>

      <ul className="mt-4 grid h-40 grid-cols-7 items-end gap-2">
        {week.days.map((day, i) => {
          const name = weekdayName.format(dates[i])
          const height = Math.min(100, (day.minutes / studyGoal.targetMinutes) * 100)
          const color = day.metTarget
            ? 'bg-emerald-500'
            : day.metMinimum
              ? 'bg-indigo-500'
              : 'bg-slate-300 dark:bg-slate-600'
          return (
            <li
              key={day.date}
              className="flex h-full flex-col items-center justify-end gap-1"
              aria-label={t('week.dayLabel', {
                day: name,
                time: day.isStudyDay ? formatDuration(day.minutes) : t('week.restDay'),
              })}
            >
              <span className="text-[0.65rem] text-slate-500 tabular-nums" aria-hidden="true">
                {day.minutes > 0 ? formatDuration(day.minutes) : ''}
              </span>
              <div
                className={`w-full rounded-t-md ${color} ${day.isFuture ? 'opacity-40' : ''}`}
                style={{ height: `${Math.max(height, day.minutes > 0 ? 4 : 1)}%` }}
                aria-hidden="true"
              />
              <span
                className={`text-xs ${day.isToday ? 'font-bold text-indigo-700 dark:text-indigo-300' : 'text-slate-500'}`}
                aria-hidden="true"
              >
                {name}
                {!day.isStudyDay && (
                  <span className="block text-[0.6rem]">{t('week.restDay')}</span>
                )}
              </span>
            </li>
          )
        })}
      </ul>

      <div className="mt-4 space-y-1 text-sm text-slate-600 dark:text-slate-400">
        <p>{t('week.daysAtMinimum', { count: week.daysAtMinimum, total: week.studyDaysSoFar })}</p>
        {average !== null && (
          <p>
            {t('week.average', { time: formatDuration(average) })}{' '}
            {average < studyGoal.targetMinutes * 0.7
              ? t('week.realistic', {
                  target: formatDuration(studyGoal.targetMinutes),
                  time: formatDuration(Math.round(average / 15) * 15 || 15),
                })
              : t('week.onTrack')}
          </p>
        )}
      </div>
    </section>
  )
}

// ── Lessons for the week, sized to the target ───────────────────────────────

function WeekLessons() {
  const { completed, targetRole, studyGoal } = useStudy()
  const { t, formatDuration } = useLocale()
  const streamLessons = useStreamLessons()
  const today = new Date()
  const budget = weeklyBudget(studyGoal, today)
  const total = Object.values(budget).reduce((sum, minutes) => sum + minutes, 0)

  // Representative days for the routine table (this week's Wednesday, Saturday, Sunday).
  const [, , wednesday, , , saturday, sunday] = weekDates(today) as Date[]
  const byStream = (date: Date) =>
    Object.fromEntries(
      planDay(studyGoal.targetMinutes, date).map((b) => [b.stream, formatDuration(b.minutes)]),
    ) as Partial<Record<Stream, string>>
  const dash = '—'
  const weekday = byStream(wednesday!)
  const sat = byStream(saturday!)
  const sun = byStream(sunday!)
  const routine = [
    {
      day: t('schedule.weekdays'),
      plan: t('schedule.routineWeekday', {
        module: weekday.module ?? dash,
        dsa: weekday.dsa ?? dash,
      }),
    },
    {
      day: t('schedule.saturday'),
      plan:
        studyGoal.studyDays >= 6
          ? t('schedule.routineSaturday', {
              architecture: sat.architecture ?? dash,
              project: sat.project ?? dash,
            })
          : t('schedule.rest'),
    },
    {
      day: t('schedule.sunday'),
      plan:
        studyGoal.studyDays === 7
          ? t('schedule.routineSunday', { module: sun.module ?? dash, dsa: sun.dsa ?? dash })
          : t('schedule.rest'),
    },
  ]

  return (
    <section className="space-y-4">
      <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800">
        <table className="w-full text-left text-sm">
          <caption className="px-4 pt-3 text-left font-semibold text-slate-900 dark:text-white">
            {t('schedule.routineHeading')}
          </caption>
          <tbody>
            {routine.map((row) => (
              <tr
                key={row.day}
                className="border-b border-slate-100 last:border-0 dark:border-slate-800"
              >
                <th className="w-32 px-4 py-2.5 font-medium text-slate-900 dark:text-white">
                  {row.day}
                </th>
                <td className="px-4 py-2.5 text-slate-600 dark:text-slate-400">{row.plan}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div>
        <h2 className="font-semibold text-slate-900 dark:text-white">
          {t('schedule.weekLessons')}
        </h2>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
          {t('schedule.weekLessonsDescription', { time: formatDuration(total) })}
        </p>
      </div>
      <div className="grid gap-5 md:grid-cols-2">
        {(Object.keys(STREAM_TITLE) as Stream[])
          .filter((stream) => budget[stream] > 0)
          .map((stream) => (
            <StreamCard
              key={stream}
              title={t(STREAM_TITLE[stream])}
              when={t('schedule.streamWeekly', { time: formatDuration(budget[stream]) })}
              lessons={pickForBudget(streamLessons(stream), completed, targetRole, budget[stream])}
            />
          ))}
      </div>
    </section>
  )
}

function StreamCard(props: { title: string; when: string; lessons: LessonMeta[] }) {
  const minutes = props.lessons.reduce((sum, lesson) => sum + lesson.durationMinutes, 0)
  const { t, formatDuration } = useLocale()

  return (
    <section className="rounded-xl border border-slate-200 p-5 dark:border-slate-800">
      <div className="flex items-baseline justify-between gap-2">
        <h3 className="font-semibold text-slate-900 dark:text-white">{props.title}</h3>
        <span className="text-xs text-slate-500">{props.when}</span>
      </div>
      {props.lessons.length === 0 ? (
        <p className="mt-3 text-sm text-slate-400 italic">{t('schedule.nothingPlanned')}</p>
      ) : (
        <>
          <ol className="mt-3 space-y-2">
            {props.lessons.map((lesson) => (
              <li key={lesson.id}>
                <Link
                  to={lesson.url}
                  className="block rounded-lg px-3 py-2 hover:bg-slate-50 dark:hover:bg-slate-900"
                >
                  <span className="block text-sm font-medium text-slate-900 dark:text-white">
                    {lesson.title}
                  </span>
                  <span className="text-xs text-slate-500">
                    ~{formatDuration(lesson.durationMinutes)}
                  </span>
                </Link>
              </li>
            ))}
          </ol>
          <p className="mt-3 text-xs text-slate-500">
            {t('schedule.planned', { time: formatDuration(minutes) })}
          </p>
        </>
      )}
    </section>
  )
}

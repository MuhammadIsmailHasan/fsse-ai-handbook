/**
 * DoneButton.tsx — mark a lesson as done (or not done).
 *
 * Teaches: `aria-pressed` for toggle buttons, so assistive tech announces the state.
 */
import { useStudy } from '../../hooks/useStudy'
import { Icon } from '../ui/Icon'

export function DoneButton({ lessonId, size = 'md' }: { lessonId: string; size?: 'sm' | 'md' }) {
  const { isDone, toggleDone } = useStudy()
  const done = isDone(lessonId)

  return (
    <button
      type="button"
      onClick={() => toggleDone(lessonId)}
      aria-pressed={done}
      className={`inline-flex items-center gap-2 rounded-lg font-medium transition ${
        size === 'sm' ? 'px-2.5 py-1 text-xs' : 'px-4 py-2 text-sm'
      } ${
        done
          ? 'bg-emerald-600 text-white hover:bg-emerald-700'
          : 'border border-slate-300 text-slate-700 hover:border-emerald-500 hover:text-emerald-700 dark:border-slate-700 dark:text-slate-200 dark:hover:text-emerald-300'
      }`}
    >
      <Icon name="check" size={size === 'sm' ? 12 : 16} />
      {done ? 'Done' : 'Mark as done'}
    </button>
  )
}

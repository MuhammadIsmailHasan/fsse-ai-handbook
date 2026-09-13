/**
 * SearchDialog.tsx — the Cmd/Ctrl + K search window.
 *
 * Teaches:
 * - Keyboard-friendly UI: ↑/↓ to move, Enter to open, Esc to close.
 * - Derived state: results are computed from `query` during render — not stored.
 * - The native <dialog> element: built-in focus trapping and Esc handling.
 */
import { useEffect, useRef, useState, type KeyboardEvent } from 'react'
import { useNavigate } from 'react-router'
import { searchLessons } from '../../lib/search'
import { Icon } from '../ui/Icon'

type SearchDialogProps = {
  open: boolean
  onClose: () => void
}

export function SearchDialog({ open, onClose }: SearchDialogProps) {
  const dialogRef = useRef<HTMLDialogElement>(null)

  // Sync the `open` prop with the real <dialog> element (an external "system").
  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return
    if (open && !dialog.open) dialog.showModal()
    if (!open && dialog.open) dialog.close()
  }, [open])

  return (
    <dialog
      ref={dialogRef}
      onClose={onClose}
      onClick={(event) => {
        // Clicking the dark backdrop (the dialog itself, not its content) closes it.
        if (event.target === dialogRef.current) onClose()
      }}
      className="mx-auto mt-[10vh] w-[min(40rem,calc(100vw-2rem))] rounded-2xl bg-white p-0 text-slate-800 shadow-2xl backdrop:bg-slate-950/60 dark:bg-slate-900 dark:text-slate-200"
    >
      {/* Mount the content only while open, so it starts fresh every time. */}
      {open && <SearchContent onClose={onClose} />}
    </dialog>
  )
}

function SearchContent({ onClose }: { onClose: () => void }) {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [activeIndex, setActiveIndex] = useState(0)

  const results = searchLessons(query)
  const safeIndex = Math.min(activeIndex, Math.max(results.length - 1, 0))

  function openResult(index: number) {
    const lesson = results[index]
    if (!lesson) return
    navigate(lesson.url)
    onClose()
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      setActiveIndex((safeIndex + 1) % Math.max(results.length, 1))
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      setActiveIndex((safeIndex - 1 + results.length) % Math.max(results.length, 1))
    } else if (event.key === 'Enter') {
      event.preventDefault()
      openResult(safeIndex)
    }
  }

  return (
    <div>
      <div className="flex items-center gap-3 border-b border-slate-200 px-4 dark:border-slate-800">
        <Icon name="search" className="text-slate-400" />
        <input
          autoFocus
          value={query}
          onChange={(event) => {
            setQuery(event.target.value)
            setActiveIndex(0)
          }}
          onKeyDown={handleKeyDown}
          placeholder="Search lessons, topics, tags…"
          aria-label="Search lessons"
          className="h-14 flex-1 bg-transparent text-base outline-none placeholder:text-slate-400"
        />
        <kbd className="rounded border border-slate-300 px-1.5 text-xs text-slate-400 dark:border-slate-700">
          Esc
        </kbd>
      </div>

      <ul className="max-h-[60vh] overflow-y-auto p-2" role="listbox" aria-label="Results">
        {query.trim().length >= 2 && results.length === 0 && (
          <li className="px-3 py-6 text-center text-sm text-slate-500">No lessons found.</li>
        )}
        {query.trim().length < 2 && (
          <li className="px-3 py-6 text-center text-sm text-slate-500">
            Type at least 2 characters.
          </li>
        )}
        {results.map((lesson, index) => (
          <li key={lesson.id} role="option" aria-selected={index === safeIndex}>
            <button
              type="button"
              onClick={() => openResult(index)}
              onMouseEnter={() => setActiveIndex(index)}
              className={`w-full rounded-lg px-3 py-2 text-left ${
                index === safeIndex ? 'bg-indigo-50 dark:bg-indigo-500/10' : ''
              }`}
            >
              <span className="block text-sm font-medium text-slate-900 dark:text-white">
                {lesson.title}
              </span>
              <span className="mt-0.5 line-clamp-1 block text-xs text-slate-500">
                {lesson.id.split('/').slice(0, -1).join(' › ')} — {lesson.summary}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}

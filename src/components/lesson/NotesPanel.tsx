/**
 * NotesPanel.tsx — private notes for a lesson, saved automatically.
 *
 * Teaches:
 * - Debouncing: wait until the user stops typing for a moment before saving,
 *   instead of writing to storage on every keystroke.
 * - Effect cleanup cancels the previous timer when the text changes again.
 */
import { useEffect, useState } from 'react'
import { readJSON, STORAGE_KEYS, writeJSON } from '../../lib/storage'

const SAVE_DELAY_MS = 500

export function NotesPanel({ lessonId }: { lessonId: string }) {
  const [text, setText] = useState(
    () => readJSON<Record<string, string>>(STORAGE_KEYS.notes, {})[lessonId] ?? '',
  )
  const [savedText, setSavedText] = useState(text)

  useEffect(() => {
    if (text === savedText) return
    const timer = window.setTimeout(() => {
      const notes = readJSON<Record<string, string>>(STORAGE_KEYS.notes, {})
      if (text.trim()) notes[lessonId] = text
      else delete notes[lessonId]
      writeJSON(STORAGE_KEYS.notes, notes)
      setSavedText(text)
    }, SAVE_DELAY_MS)
    return () => window.clearTimeout(timer)
  }, [lessonId, text, savedText])

  return (
    <section className="mt-12 rounded-xl border border-slate-200 p-5 dark:border-slate-800">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-slate-900 dark:text-white">📝 My notes</h2>
        <span className="text-xs text-slate-400" aria-live="polite">
          {text === savedText ? (text ? 'Saved' : '') : 'Saving…'}
        </span>
      </div>
      <p className="mt-1 text-sm text-slate-500">
        Write the idea in your own words. Stored only in this browser.
      </p>
      <textarea
        value={text}
        onChange={(event) => setText(event.target.value)}
        rows={5}
        placeholder="What clicked? What's still confusing? What will you try?"
        aria-label="My notes for this lesson"
        className="mt-3 w-full resize-y rounded-lg border border-slate-200 bg-white p-3 text-sm outline-none focus:border-indigo-400 dark:border-slate-700 dark:bg-slate-900"
      />
    </section>
  )
}

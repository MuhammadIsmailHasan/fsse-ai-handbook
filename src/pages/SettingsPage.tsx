/**
 * SettingsPage.tsx — app preferences and data backup.
 *
 * Teaches:
 * - Controlled inputs: the checked/selected state comes FROM React state,
 *   and `onChange` sends changes back. React is the single source of truth.
 * - A two-step "confirm" button instead of a blocking `window.confirm()` popup.
 */
import { useState, type ReactNode } from 'react'
import { PageHeader } from '../components/ui/PageHeader'
import { useStudy } from '../hooks/useStudy'
import { useTheme, type ThemePreference } from '../hooks/useTheme'
import { clearAllData, downloadBackup, restoreBackup } from '../lib/backup'
import { TARGET_ROLES } from '../lib/roles'

const THEME_OPTIONS = [
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
  { value: 'system', label: 'System' },
] as const satisfies ReadonlyArray<{ value: ThemePreference; label: string }>

const optionClass =
  'flex cursor-pointer items-start gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm has-checked:border-indigo-500 has-checked:bg-indigo-50 dark:border-slate-700 dark:has-checked:bg-indigo-500/10'

export function SettingsPage() {
  const { preference, setPreference } = useTheme()
  const { targetRole, setTargetRole, hideNotNeeded, setHideNotNeeded } = useStudy()

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <PageHeader eyebrow="App" title="Settings" />

      <Card title="🎯 Target role" description="Lessons show how important they are for this role.">
        <fieldset className="grid gap-2 sm:grid-cols-2">
          <legend className="sr-only">Target role</legend>
          {TARGET_ROLES.map((role) => (
            <label key={role.id} className={optionClass}>
              <input
                type="radio"
                name="target-role"
                checked={targetRole === role.id}
                onChange={() => setTargetRole(role.id)}
                className="mt-1 accent-indigo-600"
              />
              <span>
                <span className="block font-medium">{role.label}</span>
                <span className="block text-xs text-slate-500">{role.description}</span>
              </span>
            </label>
          ))}
        </fieldset>

        <label className="mt-4 flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={hideNotNeeded}
            onChange={(event) => setHideNotNeeded(event.target.checked)}
            className="accent-indigo-600"
          />
          Hide lessons marked ➖ “not needed” for my target role
        </label>
      </Card>

      <Card title="Theme">
        <fieldset className="flex flex-wrap gap-2">
          <legend className="sr-only">Theme</legend>
          {THEME_OPTIONS.map((option) => (
            <label key={option.value} className={optionClass}>
              <input
                type="radio"
                name="theme"
                checked={preference === option.value}
                onChange={() => setPreference(option.value)}
                className="mt-0.5 accent-indigo-600"
              />
              {option.label}
            </label>
          ))}
        </fieldset>
      </Card>

      <BackupCard />
    </div>
  )
}

function BackupCard() {
  const [message, setMessage] = useState<string | null>(null)
  const [confirmReset, setConfirmReset] = useState(false)

  async function handleImport(file: File | undefined) {
    if (!file) return
    try {
      const count = await restoreBackup(file)
      setMessage(`Restored ${count} item(s). Reloading…`)
      window.setTimeout(() => window.location.reload(), 800)
    } catch (error) {
      setMessage((error as Error).message)
    }
  }

  function handleReset() {
    if (!confirmReset) {
      setConfirmReset(true)
      return
    }
    clearAllData()
    window.location.reload()
  }

  return (
    <Card
      title="💾 Progress backup"
      description="Progress, notes and settings live only in this browser. Export a backup regularly — clearing browser data deletes them."
    >
      <div className="flex flex-wrap gap-2">
        <button type="button" onClick={downloadBackup} className={buttonClass}>
          Export progress (.json)
        </button>

        <label className={`${buttonClass} cursor-pointer`}>
          Import backup…
          <input
            type="file"
            accept="application/json,.json"
            className="sr-only"
            onChange={(event) => handleImport(event.target.files?.[0])}
          />
        </label>

        <button
          type="button"
          onClick={handleReset}
          onBlur={() => setConfirmReset(false)}
          className={`${buttonClass} ${confirmReset ? 'border-red-500 bg-red-600 text-white hover:bg-red-700' : 'text-red-600 dark:text-red-400'}`}
        >
          {confirmReset ? 'Click again to delete everything' : 'Reset all data'}
        </button>
      </div>
      {message && (
        <p className="mt-3 text-sm text-slate-600 dark:text-slate-400" role="status">
          {message}
        </p>
      )}
    </Card>
  )
}

const buttonClass =
  'rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800'

function Card(props: { title: string; description?: string; children: ReactNode }) {
  return (
    <section className="rounded-xl border border-slate-200 p-5 dark:border-slate-800">
      <h2 className="font-semibold text-slate-900 dark:text-white">{props.title}</h2>
      {props.description && (
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">{props.description}</p>
      )}
      <div className="mt-4">{props.children}</div>
    </section>
  )
}

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
import { useContent } from '../hooks/useContent'
import { useLocale } from '../hooks/useLocale'
import { useStudy } from '../hooks/useStudy'
import { useTheme, type ThemePreference } from '../hooks/useTheme'
import { clearAllData, downloadBackup, restoreBackup } from '../lib/backup'
import { LOCALE_INFO, LOCALES } from '../i18n/messages'
import { TARGET_ROLES } from '../lib/roles'

const THEME_OPTIONS = ['light', 'dark', 'system'] as const satisfies ReadonlyArray<ThemePreference>

const optionClass =
  'flex cursor-pointer items-start gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm has-checked:border-indigo-500 has-checked:bg-indigo-50 dark:border-slate-700 dark:has-checked:bg-indigo-500/10'

export function SettingsPage() {
  const { preference, setPreference } = useTheme()
  const { targetRole, setTargetRole, hideNotNeeded, setHideNotNeeded, studyGoal, setStudyGoal } =
    useStudy()
  const { locale, setLocale, t, formatDuration } = useLocale()
  const { allLessons, translatedCount } = useContent()

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <PageHeader eyebrow={t('settings.eyebrow')} title={t('settings.title')} />

      <Card title={t('settings.language')} description={t('settings.languageDescription')}>
        <fieldset className="flex flex-wrap gap-2">
          <legend className="sr-only">{t('settings.language')}</legend>
          {LOCALES.map((option) => (
            <label key={option} className={optionClass}>
              <input
                type="radio"
                name="locale"
                checked={locale === option}
                onChange={() => setLocale(option)}
                className="mt-0.5 accent-indigo-600"
              />
              {LOCALE_INFO[option].flag} {LOCALE_INFO[option].name}
            </label>
          ))}
        </fieldset>
        {locale !== 'en' && (
          <p className="mt-3 text-xs text-slate-500">
            {t('settings.translationProgress', {
              translated: translatedCount,
              total: allLessons.length,
            })}
          </p>
        )}
      </Card>

      <Card title={t('settings.goal')} description={t('settings.goalDescription')}>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="text-sm">
            <span className="block font-medium">{t('settings.target')}</span>
            <select
              value={studyGoal.targetMinutes}
              onChange={(event) => setStudyGoal({ targetMinutes: Number(event.target.value) })}
              className={selectClass}
            >
              {range(30, 600, 30).map((minutes) => (
                <option key={minutes} value={minutes}>
                  {formatDuration(minutes)}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm">
            <span className="block font-medium">{t('settings.minimum')}</span>
            <select
              value={studyGoal.minimumMinutes}
              onChange={(event) => setStudyGoal({ minimumMinutes: Number(event.target.value) })}
              className={selectClass}
            >
              {range(15, studyGoal.targetMinutes, 15).map((minutes) => (
                <option key={minutes} value={minutes}>
                  {formatDuration(minutes)}
                </option>
              ))}
            </select>
          </label>
        </div>
        <fieldset className="mt-4 flex flex-wrap gap-2">
          <legend className="mb-2 text-sm font-medium">{t('settings.studyDays')}</legend>
          {([5, 6, 7] as const).map((days) => (
            <label key={days} className={optionClass}>
              <input
                type="radio"
                name="study-days"
                checked={studyGoal.studyDays === days}
                onChange={() => setStudyGoal({ studyDays: days })}
                className="mt-0.5 accent-indigo-600"
              />
              {t(`settings.days${days}`)}
            </label>
          ))}
        </fieldset>
      </Card>

      <Card title={t('targetRole.heading')} description={t('settings.targetRoleDescription')}>
        <fieldset className="grid gap-2 sm:grid-cols-2">
          <legend className="sr-only">{t('settings.targetRoleLegend')}</legend>
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
                <span className="block text-xs text-slate-500">{t(role.descriptionKey)}</span>
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
          {t('settings.hideNotNeeded')}
        </label>
      </Card>

      <Card title={t('settings.theme')}>
        <fieldset className="flex flex-wrap gap-2">
          <legend className="sr-only">{t('settings.theme')}</legend>
          {THEME_OPTIONS.map((option) => (
            <label key={option} className={optionClass}>
              <input
                type="radio"
                name="theme"
                checked={preference === option}
                onChange={() => setPreference(option)}
                className="mt-0.5 accent-indigo-600"
              />
              {t(`theme.${option}`)}
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
  const { t } = useLocale()

  async function handleImport(file: File | undefined) {
    if (!file) return
    try {
      const count = await restoreBackup(file)
      setMessage(t('settings.restored', { count }))
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
    <Card title={t('settings.backup')} description={t('settings.backupDescription')}>
      <div className="flex flex-wrap gap-2">
        <button type="button" onClick={downloadBackup} className={buttonClass}>
          {t('settings.export')}
        </button>

        <label className={`${buttonClass} cursor-pointer`}>
          {t('settings.import')}
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
          {confirmReset ? t('settings.resetConfirm') : t('settings.reset')}
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

const selectClass =
  'mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-900'

const range = (from: number, to: number, step: number) =>
  Array.from({ length: Math.floor((to - from) / step) + 1 }, (_, i) => from + i * step)

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

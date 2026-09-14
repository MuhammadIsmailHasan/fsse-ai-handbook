/**
 * RouteErrorPage.tsx — shown when a page crashes while rendering.
 *
 * Teaches:
 * - Error boundaries via React Router's `errorElement`: one broken page
 *   doesn't blank the whole app.
 * - Narrowing `unknown`: an error can be anything, so we check before using it.
 */
import { isRouteErrorResponse, Link, useRouteError } from 'react-router'
import { useLocale } from '../hooks/useLocale'

export function RouteErrorPage() {
  const error = useRouteError()
  const { t } = useLocale()

  let message = t('error.generic')
  if (isRouteErrorResponse(error)) {
    message = `${error.status} ${error.statusText}`
  } else if (error instanceof Error) {
    message = error.message
  }

  return (
    <div className="mx-auto max-w-xl px-4 py-16">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t('error.title')}</h1>
      <pre className="mt-4 overflow-x-auto rounded-lg bg-slate-100 p-4 text-sm whitespace-pre-wrap text-red-700 dark:bg-slate-900 dark:text-red-400">
        {message}
      </pre>
      <Link
        to="/"
        className="mt-6 inline-block font-medium text-indigo-600 hover:underline dark:text-indigo-400"
      >
        {t('common.backToDashboard')}
      </Link>
    </div>
  )
}

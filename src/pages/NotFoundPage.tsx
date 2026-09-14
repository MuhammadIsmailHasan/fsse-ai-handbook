/**
 * NotFoundPage.tsx — shown for URLs that match no route (the `*` route).
 */
import { Link } from 'react-router'
import { PageHeader } from '../components/ui/PageHeader'
import { useLocale } from '../hooks/useLocale'

export function NotFoundPage() {
  const { t } = useLocale()

  return (
    <div>
      <PageHeader
        eyebrow="404"
        title={t('notFound.title')}
        description={t('notFound.description')}
      />
      <Link to="/" className="font-medium text-indigo-600 hover:underline dark:text-indigo-400">
        {t('common.backToDashboard')}
      </Link>
    </div>
  )
}

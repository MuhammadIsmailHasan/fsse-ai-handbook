/**
 * NotFoundPage.tsx — shown for URLs that match no route (the `*` route).
 */
import { Link } from 'react-router'
import { PageHeader } from '../components/ui/PageHeader'

export function NotFoundPage() {
  return (
    <div>
      <PageHeader
        eyebrow="404"
        title="Page not found"
        description="This page doesn't exist (yet)."
      />
      <Link to="/" className="font-medium text-indigo-600 hover:underline dark:text-indigo-400">
        ← Back to dashboard
      </Link>
    </div>
  )
}

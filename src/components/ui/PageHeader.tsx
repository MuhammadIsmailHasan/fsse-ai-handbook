/**
 * PageHeader.tsx — consistent title block for every page.
 *
 * Teaches: optional props (`eyebrow?`, `description?`) and rendering them
 * only when provided with `&&`.
 */
import type { ReactNode } from 'react'

type PageHeaderProps = {
  title: string
  eyebrow?: string
  description?: ReactNode
}

export function PageHeader({ title, eyebrow, description }: PageHeaderProps) {
  return (
    <header className="mb-8">
      {eyebrow && (
        <p className="mb-1 text-sm font-medium text-indigo-600 dark:text-indigo-400">{eyebrow}</p>
      )}
      <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">{title}</h1>
      {description && (
        <p className="mt-2 max-w-2xl text-slate-600 dark:text-slate-400">{description}</p>
      )}
    </header>
  )
}

/**
 * Callout.tsx — colored boxes for tips, warnings, RevoShop links, FastAPI notes…
 *
 * Markdown:
 *   :::tip[Optional title]
 *   Content here
 *   :::
 *
 * Teaches: mapping a "variant" prop to styles with a lookup object, and
 * `satisfies` to check the object's shape without losing its exact keys.
 */
import type { ReactNode } from 'react'

const VARIANTS = {
  tip: {
    icon: '💡',
    title: 'Tip',
    box: 'border-emerald-300 bg-emerald-50 dark:border-emerald-500/40 dark:bg-emerald-500/10',
  },
  note: {
    icon: '📝',
    title: 'Note',
    box: 'border-sky-300 bg-sky-50 dark:border-sky-500/40 dark:bg-sky-500/10',
  },
  warning: {
    icon: '⚠️',
    title: 'Warning',
    box: 'border-amber-300 bg-amber-50 dark:border-amber-500/40 dark:bg-amber-500/10',
  },
  danger: {
    icon: '🚨',
    title: 'Danger',
    box: 'border-red-300 bg-red-50 dark:border-red-500/40 dark:bg-red-500/10',
  },
  revoshop: {
    icon: '🔍',
    title: 'Find it in RevoShop',
    box: 'border-violet-300 bg-violet-50 dark:border-violet-500/40 dark:bg-violet-500/10',
  },
  fastapi: {
    icon: '🔄',
    title: 'In FastAPI…',
    box: 'border-teal-300 bg-teal-50 dark:border-teal-500/40 dark:bg-teal-500/10',
  },
  bahasa: {
    icon: '🇮🇩',
    title: 'Dalam Bahasa',
    box: 'border-rose-300 bg-rose-50 dark:border-rose-500/40 dark:bg-rose-500/10',
  },
} satisfies Record<string, { icon: string; title: string; box: string }>

export type CalloutVariant = keyof typeof VARIANTS

type CalloutProps = {
  variant?: string
  title?: string
  children?: ReactNode
}

function isVariant(value: string | undefined): value is CalloutVariant {
  return value !== undefined && value in VARIANTS
}

export function Callout({ variant, title, children }: CalloutProps) {
  const style = VARIANTS[isVariant(variant) ? variant : 'note']

  return (
    <aside className={`my-6 rounded-xl border-l-4 px-5 py-3 ${style.box}`}>
      <p className="not-prose mt-1 mb-1 font-semibold text-slate-900 dark:text-white">
        <span aria-hidden="true">{style.icon}</span> {title ?? style.title}
      </p>
      <div className="[&>*:first-child]:mt-1 [&>*:last-child]:mb-1">{children}</div>
    </aside>
  )
}

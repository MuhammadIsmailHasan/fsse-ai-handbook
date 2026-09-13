/**
 * TopBar.tsx — the sticky header.
 *
 * Teaches:
 * - Props with a function type: the parent decides WHAT happens on click,
 *   the child only decides WHEN to call it.
 * - `aria-label` for icon-only buttons (screen readers need a name).
 */
import { Link } from 'react-router'
import { ThemeToggle } from './ThemeToggle'
import { Icon } from '../ui/Icon'

type TopBarProps = {
  onMenuClick: () => void
  onSearchClick: () => void
}

// Show the right shortcut symbol for the user's operating system.
const isMac = typeof navigator !== 'undefined' && /Mac|iPhone|iPad/.test(navigator.userAgent)

export function TopBar({ onMenuClick, onSearchClick }: TopBarProps) {
  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/85 backdrop-blur dark:border-slate-800 dark:bg-slate-950/85">
      <div className="mx-auto flex h-14 max-w-screen-2xl items-center gap-3 px-4 sm:px-6">
        <button
          type="button"
          onClick={onMenuClick}
          className="rounded-md p-2 text-slate-600 hover:bg-slate-100 lg:hidden dark:text-slate-300 dark:hover:bg-slate-800"
          aria-label="Open navigation"
        >
          <Icon name="menu" />
        </button>

        <Link to="/" className="flex items-center gap-2 font-semibold tracking-tight">
          <img src="/favicon.svg" alt="" className="h-7 w-7" />
          <span>
            FSSE <span className="text-indigo-600 dark:text-indigo-400">Handbook</span>
          </span>
        </Link>

        <div className="ml-auto flex items-center gap-1">
          <button
            type="button"
            onClick={onSearchClick}
            className="flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-500 hover:border-slate-300 hover:text-slate-700 dark:border-slate-800 dark:hover:border-slate-700 dark:hover:text-slate-300"
          >
            <Icon name="search" size={16} />
            <span className="hidden sm:inline">Search</span>
            <kbd className="hidden rounded bg-slate-100 px-1.5 font-sans text-xs sm:inline dark:bg-slate-800">
              {isMac ? '⌘' : 'Ctrl'} K
            </kbd>
          </button>
          <ThemeToggle />
        </div>
      </div>
    </header>
  )
}

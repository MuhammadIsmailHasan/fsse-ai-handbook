/**
 * Sidebar.tsx — main navigation.
 *
 * Teaches:
 * - Rendering lists with `.map()` and a stable `key`.
 * - <NavLink>: like <Link>, but tells you if it's the active page, so we can style it.
 * - A mobile drawer: fixed + translated off-screen when closed.
 */
import type { ReactNode } from 'react'
import { NavLink } from 'react-router'
import { getLessonsInGroup } from '../../content'
import { OVERVIEW_LINKS, type NavItem } from '../../config/navigation'
import { Icon } from '../ui/Icon'
import { CourseTree, ProjectTree, TrackTree } from './CourseTree'
import { TargetRoleSummary } from './TargetRoleSummary'

type SidebarProps = {
  open: boolean
  onClose: () => void
}

export function Sidebar({ open, onClose }: SidebarProps) {
  const guides = getLessonsInGroup('guides', 'guides')

  return (
    <>
      {open && (
        <div
          className="fixed inset-0 z-40 bg-slate-950/50 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={[
          'fixed inset-y-0 left-0 z-50 w-80 overflow-y-auto border-r border-slate-200 bg-white px-3 pb-10',
          'transition-transform duration-200 dark:border-slate-800 dark:bg-slate-950',
          'lg:sticky lg:top-14 lg:z-0 lg:h-[calc(100dvh-3.5rem)] lg:translate-x-0',
          open ? 'translate-x-0' : '-translate-x-full',
        ].join(' ')}
        aria-label="Handbook navigation"
      >
        <div className="flex h-14 items-center justify-end lg:hidden">
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-2 text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
            aria-label="Close navigation"
          >
            <Icon name="close" />
          </button>
        </div>

        <nav className="space-y-6 lg:pt-5">
          <TargetRoleSummary onNavigate={onClose} />

          <NavSection title="Overview">
            <LinkList items={OVERVIEW_LINKS} onNavigate={onClose} />
          </NavSection>

          <NavSection title="Course">
            <CourseTree onNavigate={onClose} />
          </NavSection>

          <NavSection title="Tracks">
            <TrackTree onNavigate={onClose} />
          </NavSection>

          <NavSection title="Projects">
            <ProjectTree onNavigate={onClose} />
          </NavSection>

          <NavSection title="Guides & App">
            <LinkList
              items={[
                ...guides.map((guide) => ({
                  label: guide.title,
                  to: guide.url,
                  icon: 'book' as const,
                })),
                { label: 'Settings', to: '/settings', icon: 'settings' },
              ]}
              onNavigate={onClose}
            />
          </NavSection>
        </nav>
      </aside>
    </>
  )
}

function NavSection({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div>
      <h2 className="mb-2 px-3 text-xs font-semibold tracking-wider text-slate-400 uppercase dark:text-slate-500">
        {title}
      </h2>
      {children}
    </div>
  )
}

function LinkList({ items, onNavigate }: { items: NavItem[]; onNavigate: () => void }) {
  return (
    <ul className="space-y-0.5">
      {items.map((item) => (
        <li key={item.to}>
          <NavLink
            to={item.to}
            end // "/" should only be active on "/", not on every page
            onClick={onNavigate}
            className={({ isActive }) =>
              [
                'flex items-center gap-2.5 rounded-md px-3 py-1.5 text-sm',
                isActive
                  ? 'bg-indigo-50 font-medium text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-300'
                  : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800/60',
              ].join(' ')
            }
          >
            <Icon name={item.icon} size={16} />
            {item.label}
          </NavLink>
        </li>
      ))}
    </ul>
  )
}

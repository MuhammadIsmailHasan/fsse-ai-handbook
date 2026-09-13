/**
 * AppLayout.tsx — the frame around every page: top bar, sidebar, content.
 *
 * Teaches:
 * - Layout routes: <Outlet /> is where the current child page renders.
 * - Lifting state up: `sidebarOpen` lives here because BOTH TopBar (opens it)
 *   and Sidebar (closes it) need it.
 * - Responsive design with Tailwind: the sidebar is a drawer on small screens
 *   and always visible from the `lg` breakpoint.
 */
import { useState } from 'react'
import { Outlet, ScrollRestoration } from 'react-router'
import { useModHotkey } from '../../hooks/useHotkey'
import { SearchDialog } from '../search/SearchDialog'
import { Sidebar } from './Sidebar'
import { TopBar } from './TopBar'

export function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)

  useModHotkey('k', () => setSearchOpen(true))

  return (
    <div className="min-h-dvh">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:rounded focus:bg-indigo-600 focus:px-3 focus:py-2 focus:text-white"
      >
        Skip to content
      </a>

      <TopBar onMenuClick={() => setSidebarOpen(true)} onSearchClick={() => setSearchOpen(true)} />
      <SearchDialog open={searchOpen} onClose={() => setSearchOpen(false)} />

      <div className="mx-auto flex max-w-screen-2xl">
        <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main id="main" className="min-w-0 flex-1 px-4 py-8 sm:px-8 lg:px-12">
          <Outlet />
        </main>
      </div>

      {/* Restores scroll position on back/forward, scrolls to top on new pages. */}
      <ScrollRestoration />
    </div>
  )
}

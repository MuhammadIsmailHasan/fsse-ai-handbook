/**
 * navigation.ts — static sidebar links (pages that always exist).
 *
 * The course tree (modules → weeks → lessons) is NOT here: it is generated from
 * `content/course.json` so adding content never requires code changes.
 *
 * Teaches: keeping configuration (data) separate from components (UI).
 */
import type { IconName } from '../components/ui/Icon'
import type { MessageKey } from '../i18n/messages'

export type NavItem = {
  /** A message key (translated in the sidebar) or, for lessons, the title itself. */
  label: MessageKey | { text: string }
  to: string
  icon: IconName
}

export const OVERVIEW_LINKS: NavItem[] = [
  { label: 'nav.dashboard', to: '/', icon: 'home' },
  { label: 'nav.roadmap', to: '/roadmap', icon: 'map' },
  { label: 'nav.thisWeek', to: '/schedule', icon: 'calendar' },
]

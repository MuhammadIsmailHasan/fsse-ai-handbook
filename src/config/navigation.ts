/**
 * navigation.ts — static sidebar links (pages that always exist).
 *
 * The course tree (modules → weeks → lessons) is NOT here: it is generated from
 * `content/course.json` so adding content never requires code changes.
 *
 * Teaches: keeping configuration (data) separate from components (UI).
 */
import type { IconName } from '../components/ui/Icon'

export type NavItem = {
  label: string
  to: string
  icon: IconName
}

export const OVERVIEW_LINKS: NavItem[] = [
  { label: 'Dashboard', to: '/', icon: 'home' },
  { label: 'Roadmap', to: '/roadmap', icon: 'map' },
  { label: 'This Week', to: '/schedule', icon: 'calendar' },
]

export const TRACK_LINKS: NavItem[] = [
  { label: 'DSA for Interviews', to: '/tracks/dsa', icon: 'puzzle' },
  { label: 'Architecture', to: '/tracks/architecture', icon: 'building' },
]

export const PROJECT_LINKS: NavItem[] = [
  { label: 'CareerPilot', to: '/projects/careerpilot', icon: 'rocket' },
  { label: 'SupportDesk AI', to: '/projects/supportdesk-ai', icon: 'rocket' },
  { label: 'StudyMind', to: '/projects/studymind', icon: 'rocket' },
]

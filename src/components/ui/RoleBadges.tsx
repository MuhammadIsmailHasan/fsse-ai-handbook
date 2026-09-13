/**
 * RoleBadges.tsx — shows how important something is for each job role.
 *
 * Teaches: iterating over a typed object with `Object.entries`. Labels and colors
 * live in config/roles.ts so wording changes happen in one place.
 */
import { LEVEL_INFO, ROLE_INFO } from '../../config/roles'
import type { Level, RoleCode, RoleLabels } from '../../types/content'

export function RoleBadges({ roles }: { roles: RoleLabels }) {
  const entries = Object.entries(roles) as [RoleCode, Level][]

  return (
    <ul className="flex flex-wrap gap-1.5" aria-label="Importance per role">
      {entries.map(([role, level]) => (
        <li
          key={role}
          title={`${ROLE_INFO[role].name}: ${LEVEL_INFO[level].label}`}
          className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${LEVEL_INFO[level].className}`}
        >
          {ROLE_INFO[role].short}
          <span className="sr-only">:</span>
          <span className="opacity-80">{LEVEL_INFO[level].label}</span>
        </li>
      ))}
    </ul>
  )
}

/**
 * Icon.tsx — a small set of inline SVG icons (no icon library needed).
 *
 * Teaches:
 * - Union types as "allowed values": `name` can only be one of the keys below,
 *   so a typo like <Icon name="mnue" /> is a compile error.
 * - `Record<K, V>`: an object type whose keys are K and values are V.
 * - Accessibility: decorative icons get `aria-hidden` so screen readers skip them.
 */
import type { SVGProps } from 'react'

const PATHS = {
  menu: 'M4 6h16M4 12h16M4 18h16',
  close: 'M6 6l12 12M18 6L6 18',
  sun: 'M12 3v2m0 14v2m9-9h-2M5 12H3m15.36 6.36-1.42-1.42M7.05 7.05 5.64 5.64m12.72 0-1.41 1.41M7.05 16.95l-1.41 1.41M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0z',
  moon: 'M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z',
  monitor: 'M3 5h18v11H3zM8 20h8M12 16v4',
  home: 'M3 11l9-7 9 7M5 10v10h5v-6h4v6h5V10',
  map: 'M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2zm0 0v14m6-12v14',
  calendar: 'M4 6h16v14H4zM4 10h16M8 3v4m8-4v4',
  book: 'M4 5a2 2 0 0 1 2-2h14v16H6a2 2 0 0 0-2 2zm0 0v16',
  puzzle:
    'M10 3h4v3a2 2 0 1 0 4 0V3h3v7h-3a2 2 0 1 0 0 4h3v7h-7v-3a2 2 0 1 0-4 0v3H3v-7h3a2 2 0 1 0 0-4H3V3h7z',
  building: 'M4 21V8l8-5 8 5v13M9 21v-6h6v6M4 21h16',
  rocket:
    'M5 15c-1.5 1.5-2 5-2 5s3.5-.5 5-2m1-9a13 13 0 0 1 12-6 13 13 0 0 1-6 12l-3 2-5-5zm6 1a1 1 0 1 0 0-2 1 1 0 0 0 0 2z',
  settings:
    'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm8-3a8 8 0 0 0-.1-1.3l2-1.6-2-3.4-2.4 1a8 8 0 0 0-2.2-1.3L15 2h-4l-.4 2.4a8 8 0 0 0-2.2 1.3l-2.4-1-2 3.4 2 1.6a8 8 0 0 0 0 2.6l-2 1.6 2 3.4 2.4-1a8 8 0 0 0 2.2 1.3L11 22h4l.4-2.4a8 8 0 0 0 2.2-1.3l2.4 1 2-3.4-2-1.6c.1-.4.1-.9.1-1.3z',
  chevronRight: 'M9 6l6 6-6 6',
  chevronDown: 'M6 9l6 6 6-6',
  search: 'M11 18a7 7 0 1 1 0-14 7 7 0 0 1 0 14zm10 3-5-5',
  check: 'M5 12l5 5 9-10',
} as const

export type IconName = keyof typeof PATHS

type IconProps = SVGProps<SVGSVGElement> & { name: IconName; size?: number }

export function Icon({ name, size = 18, ...rest }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...rest}
    >
      <path d={PATHS[name]} />
    </svg>
  )
}

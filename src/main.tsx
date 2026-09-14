/**
 * main.tsx — the entry point. index.html loads this file first.
 *
 * Teaches: how a React app "boots":
 * 1. find a DOM element (<div id="root"> in index.html),
 * 2. create a React root on it,
 * 3. render the component tree into it.
 *
 * Providers wrap the router so every page can read shared state (like the theme).
 */
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router'
import { LocaleProvider } from './providers/LocaleProvider'
import { StudyProvider } from './providers/StudyProvider'
import { ThemeProvider } from './providers/ThemeProvider'
import { router } from './routes'
import './styles/index.css'

// `!` is TypeScript's "non-null assertion": we promise this element exists.
// It does — index.html contains <div id="root">.
const rootElement = document.getElementById('root')!

createRoot(rootElement).render(
  // StrictMode runs extra checks in development (e.g. double-invokes effects)
  // to reveal bugs early. It does nothing in production builds.
  <StrictMode>
    <ThemeProvider>
      <LocaleProvider>
        <StudyProvider>
          <RouterProvider router={router} />
        </StudyProvider>
      </LocaleProvider>
    </ThemeProvider>
  </StrictMode>,
)

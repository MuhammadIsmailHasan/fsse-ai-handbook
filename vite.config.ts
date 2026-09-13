/**
 * vite.config.ts — configuration for Vite (dev server + bundler) and Vitest (tests).
 *
 * Teaches:
 * - Plugins: React (JSX + fast refresh) and Tailwind CSS.
 * - Reading `.env` values at config time with `loadEnv`.
 * - `strictPort`: fail loudly if a port is taken instead of silently picking another one.
 */
/// <reference types="vitest/config" />
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'
import { lessonMetaPlugin } from './scripts/vite-plugin-lesson-meta.ts'

export default defineConfig(({ mode }) => {
  // The '' prefix loads ALL variables (not only VITE_*). These are used here in
  // Node only — they are NOT exposed to browser code.
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [lessonMetaPlugin(), react(), tailwindcss()],
    server: {
      port: Number(env.HANDBOOK_PORT || 5391),
      strictPort: true,
    },
    preview: {
      port: Number(env.HANDBOOK_PREVIEW_PORT || 4391),
      strictPort: true,
    },
    test: {
      include: ['src/**/*.test.ts', 'scripts/**/*.test.ts'],
    },
  }
})

/**
 * exercise-commands.ts — the terminal command that runs an exercise's checks.
 *
 * Python exercises live in `exercises/` (pytest via uv); JavaScript/TypeScript
 * exercises live in `exercises/web/` (Vitest via npx). Keeping this in one pure
 * function means every card shows the right command, and it's easy to test.
 */

export type ExerciseRunner = {
  kind: 'python' | 'web'
  /** Folder relative to the runner's working directory. */
  relative: string
  command: string
}

export function exerciseRunner(path: string): ExerciseRunner {
  const clean = path.replace(/\/+$/, '')
  if (clean.startsWith('exercises/web/')) {
    const relative = clean.slice('exercises/web/'.length)
    return { kind: 'web', relative, command: `cd exercises/web && npx vitest run ${relative}` }
  }
  const relative = clean.replace(/^exercises\//, '')
  return { kind: 'python', relative, command: `cd exercises && uv run pytest ${relative}` }
}

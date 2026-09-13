import { describe, expect, it } from 'vitest'
import { exerciseRunner } from './exercise-commands'

describe('exerciseRunner', () => {
  it('uses pytest for Python exercises', () => {
    expect(exerciseRunner('exercises/m2/w6/01-pytest-basics')).toEqual({
      kind: 'python',
      relative: 'm2/w6/01-pytest-basics',
      command: 'cd exercises && uv run pytest m2/w6/01-pytest-basics',
    })
  })

  it('uses Vitest for web exercises', () => {
    expect(exerciseRunner('exercises/web/m4/w1/04-js-basics/')).toEqual({
      kind: 'web',
      relative: 'm4/w1/04-js-basics',
      command: 'cd exercises/web && npx vitest run m4/w1/04-js-basics',
    })
  })
})

import { describe, expect, it } from 'vitest'
import {
  addDays,
  addToQueue,
  dueItems,
  recordReview,
  toDateKey,
  upcomingItems,
} from './spaced-repetition'

const day = (text: string) => {
  const [y, m, d] = text.split('-').map(Number)
  return new Date(y!, m! - 1, d!)
}
const problem = {
  id: 'two-sum',
  title: 'Pair Sum',
  lessonUrl: '/tracks/dsa/stage-3/01-two-pointers',
}

describe('dates', () => {
  it('formats local dates and adds days across month ends', () => {
    expect(toDateKey(day('2026-09-13'))).toBe('2026-09-13')
    expect(addDays('2026-09-29', 3)).toBe('2026-10-02')
  })
})

describe('spaced repetition', () => {
  it('schedules a new problem for tomorrow and never duplicates it', () => {
    const queue = addToQueue({}, problem, day('2026-09-13'))
    expect(queue['two-sum']?.nextDue).toBe('2026-09-14')
    expect(addToQueue(queue, problem, day('2026-09-20'))).toBe(queue)
  })

  it('pushes the next review further when remembered', () => {
    const item = addToQueue({}, problem, day('2026-09-13'))['two-sum']!
    const after = recordReview(item, 'remembered', day('2026-09-14'))
    expect(after.step).toBe(1)
    expect(after.nextDue).toBe('2026-09-17') // +3 days
    expect(item.step).toBe(0) // original not mutated
  })

  it('resets to 1 day when forgotten', () => {
    const item = { ...addToQueue({}, problem, day('2026-09-13'))['two-sum']!, step: 3 }
    expect(recordReview(item, 'forgot', day('2026-09-20'))).toMatchObject({
      step: 0,
      nextDue: '2026-09-21',
    })
  })

  it('marks as mastered after the last interval', () => {
    const item = { ...addToQueue({}, problem, day('2026-09-13'))['two-sum']!, step: 4 }
    expect(recordReview(item, 'remembered', day('2026-10-30')).mastered).toBe(true)
  })

  it('splits due and upcoming items', () => {
    const queue = addToQueue({}, problem, day('2026-09-13'))
    expect(dueItems(queue, day('2026-09-13'))).toHaveLength(0)
    expect(upcomingItems(queue, day('2026-09-13'))).toHaveLength(1)
    expect(dueItems(queue, day('2026-09-15'))).toHaveLength(1)
  })
})

/**
 * useStudy.ts — access the learner's progress and preferences from anywhere.
 */
import { createContext, useContext } from 'react'
import type { TargetRole } from '../lib/roles'
import type { ReviewOutcome, ReviewItem, ReviewQueue } from '../lib/spaced-repetition'
import type { StudyGoal, StudyLog } from '../lib/study-time'

export type PlacementResult = { result: 'pass' | 'study'; date: string }

export type StudyContextValue = {
  /** lessonId → ISO date when it was marked done */
  completed: Record<string, string>
  isDone: (lessonId: string) => boolean
  toggleDone: (lessonId: string) => void
  targetRole: TargetRole
  setTargetRole: (role: TargetRole) => void
  /** Hide lessons marked ➖ "not needed" for the target role. */
  hideNotNeeded: boolean
  setHideNotNeeded: (hide: boolean) => void
  /** DSA problems scheduled for spaced review */
  reviewQueue: ReviewQueue
  addToReview: (problem: Pick<ReviewItem, 'id' | 'title' | 'lessonUrl' | 'difficulty'>) => void
  reviewProblem: (problemId: string, outcome: ReviewOutcome) => void
  /** placementId (e.g. "modules/m1/w0") → result */
  placements: Record<string, PlacementResult>
  setPlacement: (placementId: string, result: PlacementResult['result'] | null) => void
  /** Daily target, minimum and study days per week. */
  studyGoal: StudyGoal
  setStudyGoal: (goal: Partial<StudyGoal>) => void
  /** Minutes actually studied per local date ("YYYY-MM-DD"). */
  studyLog: StudyLog
  addStudyMinutes: (dateKey: string, delta: number) => void
  /** ISO time the study timer was started, or null when it isn't running. */
  timerStartedAt: string | null
  startTimer: () => void
  /** Stops the timer and adds the elapsed minutes to the day it started. */
  stopTimer: () => number
}

export const StudyContext = createContext<StudyContextValue | null>(null)

export function useStudy(): StudyContextValue {
  const context = useContext(StudyContext)
  if (!context) throw new Error('useStudy() must be used inside <StudyProvider>.')
  return context
}

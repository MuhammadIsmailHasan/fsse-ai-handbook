/**
 * StudyProvider.tsx — owns progress, target role and preferences.
 *
 * Teaches:
 * - Functional state updates `setX(prev => …)`: always based on the latest value,
 *   even if several updates happen quickly.
 * - Immutability: we create a NEW object instead of mutating `prev`, which is how
 *   React notices that something changed.
 */
import { useCallback, useMemo, type ReactNode } from 'react'
import { StudyContext, type PlacementResult } from '../hooks/useStudy'
import { usePersistentState } from '../hooks/usePersistentState'
import { isTargetRole, type TargetRole } from '../lib/roles'
import {
  addToQueue,
  recordReview,
  type ReviewItem,
  type ReviewOutcome,
  type ReviewQueue,
} from '../lib/spaced-repetition'
import { STORAGE_KEYS } from '../lib/storage'

type Preferences = { targetRole: TargetRole; hideNotNeeded: boolean }

const DEFAULT_PREFERENCES: Preferences = { targetRole: 'ai-fs', hideNotNeeded: false }

export function StudyProvider({ children }: { children: ReactNode }) {
  const [completed, setCompleted] = usePersistentState<Record<string, string>>(
    STORAGE_KEYS.progress,
    {},
  )
  const [storedPreferences, setPreferences] = usePersistentState<Preferences>(
    STORAGE_KEYS.preferences,
    DEFAULT_PREFERENCES,
  )

  const [reviewQueue, setReviewQueue] = usePersistentState<ReviewQueue>(
    STORAGE_KEYS.reviewQueue,
    {},
  )
  const [placements, setPlacements] = usePersistentState<Record<string, PlacementResult>>(
    STORAGE_KEYS.placement,
    {},
  )

  // Stored data could be old or edited by hand — never trust it blindly.
  const targetRole = isTargetRole(storedPreferences.targetRole)
    ? storedPreferences.targetRole
    : DEFAULT_PREFERENCES.targetRole
  const hideNotNeeded = storedPreferences.hideNotNeeded === true

  const toggleDone = useCallback(
    (lessonId: string) => {
      setCompleted((prev) => {
        const next = { ...prev }
        if (next[lessonId]) delete next[lessonId]
        else next[lessonId] = new Date().toISOString()
        return next
      })
    },
    [setCompleted],
  )

  const addToReview = useCallback(
    (problem: Pick<ReviewItem, 'id' | 'title' | 'lessonUrl' | 'difficulty'>) =>
      setReviewQueue((prev) => addToQueue(prev, problem, new Date())),
    [setReviewQueue],
  )

  const reviewProblem = useCallback(
    (problemId: string, outcome: ReviewOutcome) =>
      setReviewQueue((prev) => {
        const item = prev[problemId]
        return item ? { ...prev, [problemId]: recordReview(item, outcome, new Date()) } : prev
      }),
    [setReviewQueue],
  )

  const setPlacement = useCallback(
    (placementId: string, result: PlacementResult['result'] | null) =>
      setPlacements((prev) => {
        const next = { ...prev }
        if (result === null) delete next[placementId]
        else next[placementId] = { result, date: new Date().toISOString() }
        return next
      }),
    [setPlacements],
  )

  const value = useMemo(
    () => ({
      completed,
      isDone: (lessonId: string) => Boolean(completed[lessonId]),
      toggleDone,
      targetRole,
      setTargetRole: (role: TargetRole) =>
        setPreferences((prev) => ({ ...prev, targetRole: role })),
      hideNotNeeded,
      setHideNotNeeded: (hide: boolean) =>
        setPreferences((prev) => ({ ...prev, hideNotNeeded: hide })),
      reviewQueue,
      addToReview,
      reviewProblem,
      placements,
      setPlacement,
    }),
    [
      completed,
      toggleDone,
      targetRole,
      hideNotNeeded,
      setPreferences,
      reviewQueue,
      addToReview,
      reviewProblem,
      placements,
      setPlacement,
    ],
  )

  return <StudyContext.Provider value={value}>{children}</StudyContext.Provider>
}

/**
 * routes.tsx — maps URLs to pages.
 *
 * Teaches (React Router):
 * - Nested routes: every page renders INSIDE <AppLayout> through its <Outlet />.
 * - URL params: `:moduleId` becomes available via `useParams()` in the page.
 * - `index: true` is the page shown at the parent's exact path ("/").
 * - `errorElement` catches errors thrown while rendering a route.
 */
import { createBrowserRouter } from 'react-router'
import { AppLayout } from './components/layout/AppLayout'
import { DashboardPage } from './pages/DashboardPage'
import { LessonPage } from './pages/LessonPage'
import { ModulePage } from './pages/ModulePage'
import { NotFoundPage } from './pages/NotFoundPage'
import { ProjectPage } from './pages/ProjectPage'
import { ReviewQueuePage } from './pages/ReviewQueuePage'
import { RoadmapPage } from './pages/RoadmapPage'
import { RouteErrorPage } from './pages/RouteErrorPage'
import { SchedulePage } from './pages/SchedulePage'
import { SettingsPage } from './pages/SettingsPage'
import { TrackPage } from './pages/TrackPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    errorElement: <RouteErrorPage />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'roadmap', element: <RoadmapPage /> },
      { path: 'modules/:moduleId', element: <ModulePage /> },
      { path: 'modules/:moduleId/:weekId/:lessonSlug', element: <LessonPage /> },
      // More specific paths win: "/tracks/dsa/review" matches this, not ":trackId".
      { path: 'tracks/dsa/review', element: <ReviewQueuePage /> },
      { path: 'tracks/:trackId', element: <TrackPage /> },
      { path: 'tracks/:trackId/:stageId/:lessonSlug', element: <LessonPage /> },
      { path: 'projects/:projectId', element: <ProjectPage /> },
      { path: 'projects/:projectId/:lessonSlug', element: <LessonPage /> },
      { path: 'guides/:lessonSlug', element: <LessonPage /> },
      { path: 'schedule', element: <SchedulePage /> },
      { path: 'settings', element: <SettingsPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])

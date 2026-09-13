/**
 * TrackPage.tsx — overview of a parallel track (DSA or Architecture).
 */
import { Link, useParams } from 'react-router'
import { SectionedLessonList } from '../components/lesson/SectionedLessonList'
import { PageHeader } from '../components/ui/PageHeader'
import { getLessonsInSection, getTrack } from '../content'
import { NotFoundPage } from './NotFoundPage'

export function TrackPage() {
  const { trackId = '' } = useParams()
  const track = getTrack(trackId)

  if (!track) return <NotFoundPage />

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader eyebrow="Parallel track" title={track.title} description={track.summary} />
      {track.id === 'dsa' && (
        <Link
          to="/tracks/dsa/review"
          className="-mt-4 mb-8 inline-block text-sm font-medium text-indigo-600 hover:underline dark:text-indigo-400"
        >
          🔁 Open review queue →
        </Link>
      )}
      <SectionedLessonList
        sections={track.stages.map((stage) => ({
          id: stage.id,
          title: stage.title,
          summary: stage.summary,
          note: stage.startsWith ? `Starts alongside ${stage.startsWith}` : undefined,
          lessons: getLessonsInSection('tracks', track.id, stage.id),
        }))}
      />
    </div>
  )
}

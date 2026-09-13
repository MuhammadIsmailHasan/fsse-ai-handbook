/**
 * ModulePage.tsx — overview of one module: summary, role importance, weeks and lessons.
 *
 * Teaches: reading URL params with `useParams()`, and handling the "not found" case first
 * (an "early return") so the rest of the component can assume the data exists.
 */
import { useParams } from 'react-router'
import { SectionedLessonList } from '../components/lesson/SectionedLessonList'
import { PageHeader } from '../components/ui/PageHeader'
import { RoleBadges } from '../components/ui/RoleBadges'
import { getLessonsInSection, getModule } from '../content'
import { NotFoundPage } from './NotFoundPage'

const SOURCE_LABEL = {
  core: '📘 Based on the the bootcamp outline',
  original: '🔥 Bonus module',
  mixed: '📘 the bootcamp outline + 🔥 bonus lessons',
}

export function ModulePage() {
  const { moduleId = '' } = useParams()
  const module = getModule(moduleId)

  if (!module) return <NotFoundPage />

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader
        eyebrow={`Module ${module.number} · ${SOURCE_LABEL[module.source]}`}
        title={module.title}
        description={module.summary}
      />
      <div className="-mt-4 mb-8">
        <RoleBadges roles={module.roles} />
      </div>
      <SectionedLessonList
        sections={module.weeks.map((week) => ({
          id: week.id,
          title: `${week.id.toUpperCase()} · ${week.title}`,
          summary: week.summary,
          lessons: getLessonsInSection('modules', module.id, week.id),
        }))}
      />
    </div>
  )
}

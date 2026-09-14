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
import { useContent } from '../hooks/useContent'
import { useLocale } from '../hooks/useLocale'
import { NotFoundPage } from './NotFoundPage'

const SOURCE_LABEL = {
  core: 'module.sourceCore',
  original: 'module.sourceOriginal',
  mixed: 'module.sourceMixed',
} as const

export function ModulePage() {
  const { moduleId = '' } = useParams()
  const { getLessonsInSection, getModule } = useContent()
  const { t } = useLocale()
  const module = getModule(moduleId)

  if (!module) return <NotFoundPage />

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader
        eyebrow={t('module.eyebrow', {
          number: module.number,
          source: t(SOURCE_LABEL[module.source]),
        })}
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

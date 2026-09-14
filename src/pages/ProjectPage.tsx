/**
 * ProjectPage.tsx — a portfolio project and its pages (brief, phases…).
 */
import { useParams } from 'react-router'
import { SectionedLessonList } from '../components/lesson/SectionedLessonList'
import { PageHeader } from '../components/ui/PageHeader'
import { useContent } from '../hooks/useContent'
import { useLocale } from '../hooks/useLocale'
import { NotFoundPage } from './NotFoundPage'

const KIND_LABEL = {
  main: 'project.main',
  standalone: 'project.standalone',
  practice: 'project.practice',
} as const

export function ProjectPage() {
  const { projectId = '' } = useParams()
  const { getLessonsInGroup, getProject } = useContent()
  const { t } = useLocale()
  const project = getProject(projectId)

  if (!project) return <NotFoundPage />

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader
        eyebrow={t(KIND_LABEL[project.kind])}
        title={project.title}
        description={project.tagline}
      />
      <SectionedLessonList
        sections={[
          {
            id: 'pages',
            title: t('project.pages'),
            lessons: getLessonsInGroup('projects', project.id),
          },
        ]}
      />
    </div>
  )
}

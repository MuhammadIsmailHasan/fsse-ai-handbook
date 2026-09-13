/**
 * ProjectPage.tsx — a portfolio project and its pages (brief, phases…).
 */
import { useParams } from 'react-router'
import { SectionedLessonList } from '../components/lesson/SectionedLessonList'
import { PageHeader } from '../components/ui/PageHeader'
import { getLessonsInGroup, getProject } from '../content'
import { NotFoundPage } from './NotFoundPage'

const KIND_LABEL = {
  main: '⭐ Main portfolio project',
  standalone: '🧠 Standalone AI project',
  practice: '📚 Extra practice project',
}

export function ProjectPage() {
  const { projectId = '' } = useParams()
  const project = getProject(projectId)

  if (!project) return <NotFoundPage />

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader
        eyebrow={KIND_LABEL[project.kind]}
        title={project.title}
        description={project.tagline}
      />
      <SectionedLessonList
        sections={[
          {
            id: 'pages',
            title: 'Brief & phases',
            lessons: getLessonsInGroup('projects', project.id),
          },
        ]}
      />
    </div>
  )
}

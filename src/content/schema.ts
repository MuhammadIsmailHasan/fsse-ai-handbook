/**
 * schema.ts — the SHAPE of our content, described with Zod.
 *
 * Teaches:
 * - Static types vs runtime validation: TypeScript checks code you write, but
 *   Markdown files and JSON are data read at runtime. Zod checks that data and
 *   gives a TypeScript type for free via `z.infer`.
 * - "Single source of truth": the schema defines the type, so they can't drift apart.
 *
 * This file is shared by the browser app, the Vite plugin and scripts, so it must
 * stay "pure" (no DOM, no Node APIs).
 */
import { z } from 'zod'

// ── Roles ─────────────────────────────────────────────────────────────────────

export const ROLE_CODES = ['be', 'fe', 'fs', 'ai', 'ops'] as const
export const LEVELS = ['core', 'recommended', 'optional', 'none'] as const

const levelSchema = z.enum(LEVELS)

export const roleLabelsSchema = z.strictObject({
  be: levelSchema,
  fe: levelSchema,
  fs: levelSchema,
  ai: levelSchema,
  ops: levelSchema,
})

// ── Lesson frontmatter (the YAML block at the top of every .md file) ─────────

export const LESSON_TYPES = [
  'lesson',
  'placement-check',
  'project',
  'case-study',
  'career',
  'guide',
] as const

export const lessonFrontmatterSchema = z
  .strictObject({
    title: z.string().min(1),
    summary: z.string().min(1).max(240),
    type: z.enum(LESSON_TYPES),
    source: z.enum(['core', 'original']),
    sourceRef: z.string().optional(),
    split: z.boolean().default(false),
    roles: roleLabelsSchema,
    durationMinutes: z.number().int().positive(),
    tags: z.array(z.string()).default([]),
    lastReviewed: z
      .string()
      .regex(/^\d{4}-\d{2}$/, 'Use YYYY-MM, e.g. 2026-09')
      .optional(),
    awsCost: z.enum(['free', 'small', 'concept']).optional(),
    draft: z.boolean().default(false),
  })
  .refine((data) => data.source !== 'core' || Boolean(data.sourceRef), {
    message: 'sourceRef is required when source is "core"',
    path: ['sourceRef'],
  })

// ── course.json (modules, weeks, tracks, projects) ───────────────────────────

const sectionSchema = z.strictObject({
  id: z.string().regex(/^[a-z0-9-]+$/),
  title: z.string().min(1),
  summary: z.string().optional(),
})

export const courseSchema = z.strictObject({
  modules: z.array(
    z.strictObject({
      id: z.string().regex(/^m\d+$/),
      number: z.number().int().positive(),
      title: z.string().min(1),
      source: z.enum(['core', 'original', 'mixed']),
      sourceRef: z.string().optional(),
      summary: z.string().min(1),
      roles: roleLabelsSchema,
      weeks: z.array(sectionSchema),
    }),
  ),
  tracks: z.array(
    z.strictObject({
      id: z.string().regex(/^[a-z0-9-]+$/),
      title: z.string().min(1),
      summary: z.string().min(1),
      stages: z.array(sectionSchema.extend({ startsWith: z.string().optional() })),
    }),
  ),
  projects: z.array(
    z.strictObject({
      id: z.string().regex(/^[a-z0-9-]+$/),
      title: z.string().min(1),
      tagline: z.string().min(1),
      kind: z.enum(['main', 'standalone', 'practice']),
    }),
  ),
  /** Job-ready milestones. `include` lists lesson-id prefixes, e.g. "modules/m1". */
  milestones: z.array(
    z.strictObject({
      id: z.string().regex(/^[a-z0-9-]+$/),
      title: z.string().min(1),
      applyFor: z.string().min(1),
      estimate: z.string().min(1),
      include: z.array(z.string().min(1)),
    }),
  ),
  /** Recommended order per study stream (lesson-id prefixes). Drives "This Week". */
  studyPath: z.strictObject({
    module: z.array(z.string().min(1)),
    dsa: z.array(z.string().min(1)),
    architecture: z.array(z.string().min(1)),
    project: z.array(z.string().min(1)),
  }),
})

/**
 * headings.ts — read the headings of rendered lesson content for the table of contents.
 *
 * The ids come from rehype-slug, so reading them from the DOM guarantees the
 * links match the real anchors.
 */
export type TocHeading = { id: string; text: string; level: 2 | 3 }

export function collectHeadings(container: HTMLElement): TocHeading[] {
  return [...container.querySelectorAll<HTMLHeadingElement>('h2[id], h3[id]')].map((element) => ({
    id: element.id,
    text: element.textContent ?? '',
    level: element.tagName === 'H3' ? 3 : 2,
  }))
}

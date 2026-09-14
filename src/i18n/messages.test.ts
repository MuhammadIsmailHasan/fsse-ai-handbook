/**
 * messages.test.ts — keeps the two dictionaries in step.
 *
 * TypeScript already guarantees every key exists in both languages.
 * These tests catch what types can't: a translation that forgot a {placeholder}.
 */
import { describe, expect, it } from 'vitest'
import { en, id, translate, type MessageKey } from './messages'

const placeholders = (text: string) => [...text.matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort()

describe('messages', () => {
  it('uses the same placeholders in English and Indonesian', () => {
    for (const key of Object.keys(en) as MessageKey[]) {
      expect(placeholders(id[key]), key).toEqual(placeholders(en[key]))
    }
  })

  it('has no empty translations', () => {
    for (const key of Object.keys(en) as MessageKey[]) {
      expect(id[key].trim(), key).not.toBe('')
    }
  })

  it('fills in placeholders and leaves unknown ones visible', () => {
    expect(translate('id', 'list.done', { done: 2, total: 5 })).toBe('2/5 selesai')
    expect(translate('en', 'list.done', { done: 2 })).toBe('2/{total} done')
  })
})

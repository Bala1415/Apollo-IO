import { getAllCategories, getAllInterests } from '@ai-browser-intelligence/taxonomy'
import type { TaxonomyCategory, TaxonomyInterest } from '@ai-browser-intelligence/taxonomy'
import { createLogger } from '@/logger'

const logger = createLogger('TaxonomyLoader')

let categoriesCache: TaxonomyCategory[] | null = null
let interestsCache: TaxonomyInterest[] | null = null

export function loadCategories(): TaxonomyCategory[] {
  if (!categoriesCache) {
    categoriesCache = getAllCategories()
    logger.debug('Categories loaded', { count: categoriesCache.length })
  }
  return categoriesCache
}

export function loadInterests(): TaxonomyInterest[] {
  if (!interestsCache) {
    interestsCache = getAllInterests()
    logger.debug('Interests loaded', { count: interestsCache.length })
  }
  return interestsCache
}

export function clearTaxonomyCache(): void {
  categoriesCache = null
  interestsCache = null
}

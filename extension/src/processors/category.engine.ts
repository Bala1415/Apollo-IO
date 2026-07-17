import type { ICategoryEngine } from './interfaces/processor.interface'
import { loadCategories } from '@/config'
import { CATEGORY_IDS } from '@ai-browser-intelligence/taxonomy'
import { createLogger } from '@/logger'
import { TaxonomyEngine } from './taxonomy.engine'

const logger = createLogger('CategoryEngine')
const taxonomyEngine = new TaxonomyEngine()

export class CategoryEngine implements ICategoryEngine {
  async classify(domain: string): Promise<string> {
    // 1. Check local static mapping first
    const mappedCategory = taxonomyEngine.getCategoryForDomain(domain)
    if (mappedCategory) {
      return mappedCategory
    }

    // 2. Fallback to category definition patterns
    const categories = loadCategories()
    for (const category of categories) {
      if (category.domainPatterns.some((pattern) => domain.includes(pattern))) {
        return category.id
      }
    }

    logger.debug('Domain unclassified, using UNKNOWN', { domain })
    return CATEGORY_IDS.UNKNOWN
  }

  async classifyBatch(domains: string[]): Promise<Map<string, string>> {
    const results = new Map<string, string>()
    const classifications = await Promise.all(
      domains.map(async (domain) => ({ domain, categoryId: await this.classify(domain) }))
    )
    for (const { domain, categoryId } of classifications) {
      results.set(domain, categoryId)
    }
    return results
  }
}

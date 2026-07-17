import taxonomyConfig from '@/config/taxonomy.json'
import { CATEGORY_IDS } from '@ai-browser-intelligence/taxonomy'

export class TaxonomyEngine {
  private domainMap: Map<string, string>

  constructor() {
    this.domainMap = new Map(Object.entries(taxonomyConfig))
  }

  getCategoryForDomain(domain: string): string | null {
    // 1. Direct match
    if (this.domainMap.has(domain)) {
      return this.domainMap.get(domain)!
    }
    
    // 2. Subdomain check (e.g. app.hubspot.com -> hubspot.com)
    const parts = domain.split('.')
    if (parts.length > 2) {
      const rootDomain = parts.slice(-2).join('.')
      if (this.domainMap.has(rootDomain)) {
        return this.domainMap.get(rootDomain)!
      }
    }

    return null
  }
}

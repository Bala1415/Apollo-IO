import type { ProcessedHistoryEntry } from '@ai-browser-intelligence/shared-types'
import type { RawHistoryEntry } from '@/collectors/history.collector'
import type { IHistoryProcessor } from './interfaces/processor.interface'
import { createLogger } from '@/logger'
import { DomainExtractor } from './domain.extractor'
import { CategoryEngine } from './category.engine'
import { CATEGORY_IDS, getCategoryById } from '@ai-browser-intelligence/taxonomy'

const logger = createLogger('HistoryProcessor')
const extractor = new DomainExtractor()
const categoryEngine = new CategoryEngine()

const IGNORED_DOMAINS = [
  'google.com',
  'youtube.com',
  'facebook.com',
  'instagram.com',
  'whatsapp.com',
  'twitter.com',
  'x.com',
  'netflix.com',
  'amazon.com',
  'flipkart.com',
]

export class HistoryProcessor implements IHistoryProcessor {
  async process(entries: RawHistoryEntry[]): Promise<ProcessedHistoryEntry[]> {
    logger.info('Processing history entries', { count: entries.length })
    const filtered = this.filter(entries)
    const normalized = await this.normalize(filtered)
    return this.deduplicate(normalized)
  }

  async normalize(entries: RawHistoryEntry[]): Promise<ProcessedHistoryEntry[]> {
    const domains = Array.from(new Set(entries.map(e => extractor.extractHostname(e.url) || e.domain)))
    const categoryMap = await categoryEngine.classifyBatch(domains)

    return entries.map((entry) => {
      const hostname = extractor.extractHostname(entry.url) || entry.domain
      const domain = hostname.toLowerCase()
      const date = new Date(entry.lastVisitTime)
      const categoryId = categoryMap.get(domain) || CATEGORY_IDS.UNKNOWN
      const category = getCategoryById(categoryId)
      
      const isWorkRelated = category?.parentId === CATEGORY_IDS.BUSINESS || category?.parentId === CATEGORY_IDS.TECHNOLOGY || category?.id === CATEGORY_IDS.BUSINESS || category?.id === CATEGORY_IDS.TECHNOLOGY
      const isSocialMedia = categoryId === CATEGORY_IDS.SOCIAL_MEDIA
      const isNewsMedia = categoryId === CATEGORY_IDS.NEWS
      
      return {
        id: crypto.randomUUID(),
        domain,
        categoryId,
        visitCount: entry.visitCount,
        timeSpentSeconds: 0, // Estimated later
        lastVisitedAt: entry.timestamp,
        dayOfWeek: date.getDay(),
        hourOfDay: date.getHours(),
        isWorkRelated,
        isSocialMedia,
        isNewsMedia,
      }
    })
  }

  deduplicate(entries: ProcessedHistoryEntry[]): ProcessedHistoryEntry[] {
    const domainMap = new Map<string, ProcessedHistoryEntry>()

    for (const entry of entries) {
      const existing = domainMap.get(entry.domain)
      if (existing) {
        domainMap.set(entry.domain, {
          ...existing,
          visitCount: existing.visitCount + entry.visitCount,
          lastVisitedAt: new Date(entry.lastVisitedAt) > new Date(existing.lastVisitedAt) ? entry.lastVisitedAt : existing.lastVisitedAt,
        })
      } else {
        domainMap.set(entry.domain, entry)
      }
    }

    return Array.from(domainMap.values())
  }

  filter(entries: RawHistoryEntry[]): RawHistoryEntry[] {
    return entries.filter((entry) => {
      if (extractor.isInternalUrl(entry.url)) return false
      
      const hostname = extractor.extractHostname(entry.url)
      if (!hostname) return false

      const isIgnored = IGNORED_DOMAINS.some((ignored) => hostname.includes(ignored))
      if (isIgnored) return false

      if (hostname.includes('bank') || hostname.endsWith('.gov') || hostname.endsWith('.mil')) {
        return false
      }

      return entry.domain.length > 0 && entry.visitCount > 0
    })
  }
}


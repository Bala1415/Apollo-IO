import type { ExtensionConfiguration } from '@ai-browser-intelligence/shared-types'
import type { ICollector, CollectorResult } from './interfaces/collector.interface'
import { createLogger } from '@/logger'
import { extractDomain } from '@/utils'

const logger = createLogger('HistoryCollector')

export interface RawHistoryEntry {
  url: string
  title: string
  visitCount: number
  lastVisitTime: number
  domain: string
  timestamp: string
}

export class HistoryCollector implements ICollector<RawHistoryEntry[]> {
  async isAvailable(): Promise<boolean> {
    try {
      return await chrome.permissions.contains({ permissions: ['history'] })
    } catch {
      return false
    }
  }

  reset(): void {
    logger.debug('HistoryCollector reset')
  }

  async collect(config: ExtensionConfiguration): Promise<RawHistoryEntry[]> {
    logger.info('HistoryCollector.collect called', { lookbackDays: config.historyLookbackDays })
    
    if (!(await this.isAvailable())) {
      logger.warn('History permission not granted')
      return []
    }

    const lookbackTime = Date.now() - (config.historyLookbackDays * 24 * 60 * 60 * 1000)
    
    return new Promise((resolve) => {
      chrome.history.search(
        {
          text: '',
          startTime: lookbackTime,
          maxResults: 10000 // Configurable limit could go here
        },
        (results) => {
          if (chrome.runtime.lastError) {
            logger.error('Failed to read history', chrome.runtime.lastError)
            resolve([])
            return
          }

          const entries: RawHistoryEntry[] = results
            .filter((item) => item.url)
            .map((item) => ({
              url: item.url!,
              title: item.title ?? '',
              visitCount: item.visitCount ?? 1,
              lastVisitTime: item.lastVisitTime ?? Date.now(),
              domain: extractDomain(item.url!) ?? '',
              timestamp: new Date(item.lastVisitTime ?? Date.now()).toISOString()
            }))
          
          logger.info(`Collected ${entries.length} history entries`)
          resolve(entries)
        }
      )
    })
  }

  async collectWithMeta(config: ExtensionConfiguration): Promise<CollectorResult<RawHistoryEntry[]>> {
    const start = Date.now()
    try {
      const data = await this.collect(config)
      return {
        collectorName: 'HistoryCollector',
        data,
        collectedAt: new Date().toISOString(),
        durationMs: Date.now() - start,
        success: true,
      }
    } catch (error) {
      return {
        collectorName: 'HistoryCollector',
        data: [],
        collectedAt: new Date().toISOString(),
        durationMs: Date.now() - start,
        success: false,
        error: String(error),
      }
    }
  }
}

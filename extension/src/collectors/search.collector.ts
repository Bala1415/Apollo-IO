import type { ExtensionConfiguration } from '@ai-browser-intelligence/shared-types'
import type { ICollector, CollectorResult } from './interfaces/collector.interface'
import { createLogger } from '@/logger'

const logger = createLogger('SearchCollector')

export interface SearchIntent {
  readonly categoryId: string
  readonly intentStrength: number
  readonly timestamp: string
}

export class SearchCollector implements ICollector<SearchIntent[]> {
  async isAvailable(): Promise<boolean> {
    return chrome.permissions.contains({ permissions: ['history'] })
  }

  reset(): void {
    logger.debug('SearchCollector reset')
  }

  async collect(_config: ExtensionConfiguration): Promise<SearchIntent[]> {
    logger.info('SearchCollector.collect called — implementation pending')
    return []
  }

  async collectWithMeta(_config: ExtensionConfiguration): Promise<CollectorResult<SearchIntent[]>> {
    return {
      collectorName: 'SearchCollector',
      data: [],
      collectedAt: new Date().toISOString(),
      durationMs: 0,
      success: true,
    }
  }
}

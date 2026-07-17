import type { ExtensionConfiguration } from '@ai-browser-intelligence/shared-types'
import type { ICollector, CollectorResult } from './interfaces/collector.interface'
import { createLogger } from '@/logger'
import { extractDomain } from '@/utils'

const logger = createLogger('TabsCollector')

export interface ActiveTabInfo {
  readonly url: string
  readonly domain: string
  readonly hostname: string
  readonly title: string
  readonly tabId: number
  readonly windowId: number
  readonly lastUpdated: string
}

export class TabsCollector implements ICollector<ActiveTabInfo[]> {
  async isAvailable(): Promise<boolean> {
    try {
      return await chrome.permissions.contains({ permissions: ['tabs'] })
    } catch {
      return false
    }
  }

  reset(): void {
    logger.debug('TabsCollector reset')
  }

  async collect(_config: ExtensionConfiguration): Promise<ActiveTabInfo[]> {
    logger.debug('TabsCollector.collect called')

    if (!(await this.isAvailable())) {
      logger.warn('Tabs permission not granted')
      return []
    }

    return new Promise((resolve) => {
      chrome.tabs.query({ active: true }, (tabs) => {
        if (chrome.runtime.lastError) {
          logger.error('Failed to query active tabs', chrome.runtime.lastError)
          resolve([])
          return
        }

        const activeTabs: ActiveTabInfo[] = tabs
          .filter((tab) => tab.url && tab.id !== undefined && tab.windowId !== undefined)
          .map((tab) => {
            const urlObj = new URL(tab.url!)
            return {
              url: tab.url!,
              domain: extractDomain(tab.url!) ?? urlObj.hostname,
              hostname: urlObj.hostname,
              title: tab.title ?? '',
              tabId: tab.id!,
              windowId: tab.windowId!,
              lastUpdated: new Date().toISOString()
            }
          })

        resolve(activeTabs)
      })
    })
  }

  async collectWithMeta(config: ExtensionConfiguration): Promise<CollectorResult<ActiveTabInfo[]>> {
    const start = Date.now()
    try {
      const data = await this.collect(config)
      return {
        collectorName: 'TabsCollector',
        data,
        collectedAt: new Date().toISOString(),
        durationMs: Date.now() - start,
        success: true,
      }
    } catch (error) {
      return {
        collectorName: 'TabsCollector',
        data: [],
        collectedAt: new Date().toISOString(),
        durationMs: Date.now() - start,
        success: false,
        error: String(error),
      }
    }
  }
}


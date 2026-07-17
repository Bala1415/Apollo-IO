import type { ExtensionConfiguration } from '@ai-browser-intelligence/shared-types'
import { createLogger } from '@/logger'
import { HistoryCollector } from './history.collector'
import { TabsCollector } from './tabs.collector'
import { SessionCollector } from './session.collector'
import { SearchCollector } from './search.collector'

const logger = createLogger('BrowserCollector')

export class BrowserCollector {
  readonly history: HistoryCollector
  readonly tabs: TabsCollector
  readonly session: SessionCollector
  readonly search: SearchCollector

  constructor() {
    this.history = new HistoryCollector()
    this.tabs = new TabsCollector()
    this.session = new SessionCollector()
    this.search = new SearchCollector()
  }

  async collectAll(config: ExtensionConfiguration) {
    logger.info('Starting full collection cycle')
    const start = Date.now()

    const [historyResult, tabsResult, sessionResult, searchResult] = await Promise.allSettled([
      config.featureFlags.historyCollectionEnabled
        ? this.history.collectWithMeta(config)
        : Promise.resolve(null),
      config.featureFlags.tabCollectionEnabled
        ? this.tabs.collectWithMeta(config)
        : Promise.resolve(null),
      config.featureFlags.sessionTrackingEnabled
        ? this.session.collectWithMeta(config)
        : Promise.resolve(null),
      config.featureFlags.searchCollectionEnabled
        ? this.search.collectWithMeta(config)
        : Promise.resolve(null),
    ])

    logger.info('Collection cycle complete', {
      durationMs: Date.now() - start,
      history: historyResult.status,
      tabs: tabsResult.status,
      session: sessionResult.status,
      search: searchResult.status,
    })

    return { historyResult, tabsResult, sessionResult, searchResult }
  }
}

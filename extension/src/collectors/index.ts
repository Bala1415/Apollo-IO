export type { ICollector, CollectorResult } from './interfaces/collector.interface'
export { HistoryCollector } from './history.collector'
export { TabsCollector } from './tabs.collector'
export type { ActiveTabInfo } from './tabs.collector'
export { SessionCollector } from './session.collector'
export { SearchCollector } from './search.collector'
export type { SearchIntent } from './search.collector'
export { BrowserCollector } from './browser.collector'

import { BrowserCollector } from './browser.collector'
import type { ExtensionConfiguration } from '@ai-browser-intelligence/shared-types'
import { createLogger } from '@/logger'

const logger = createLogger('Collectors')

export async function initializeCollectors(_config: ExtensionConfiguration): Promise<void> {
  logger.info('Initializing collectors')
  const _collector = new BrowserCollector()
  logger.info('Collectors initialized')
}

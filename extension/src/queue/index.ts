export { QueueManager } from './queue.manager'

import { QueueManager } from './queue.manager'
import type { ExtensionConfiguration } from '@ai-browser-intelligence/shared-types'
import { createLogger } from '@/logger'

const logger = createLogger('Queue')

export async function initializeQueue(config: ExtensionConfiguration): Promise<void> {
  logger.info('Initializing queue manager')
  const manager = new QueueManager()
  manager.initialize(config)
  const stats = await manager.getStats()
  logger.info('Queue initialized', { pending: stats.pendingItems, total: stats.totalItems })
}

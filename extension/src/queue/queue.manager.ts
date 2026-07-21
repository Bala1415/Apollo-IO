import type { QueueItem, QueueStats, BrowserPayload, QueueItemStatus } from '@ai-browser-intelligence/shared-types'
import type { ExtensionConfiguration } from '@ai-browser-intelligence/shared-types'
import { STORAGE_KEYS, RETRY_CONFIG } from '@/config'
import { createLogger } from '@/logger'

const logger = createLogger('QueueManager')

export class QueueManager {
  private config: ExtensionConfiguration | null = null

  initialize(config: ExtensionConfiguration): void {
    this.config = config
    logger.info('QueueManager initialized', { maxSize: config.maxQueueSize })
  }

  async enqueue(payload: BrowserPayload): Promise<QueueItem> {
    const item: QueueItem = {
      id: `qi_${Date.now()}_${Math.random().toString(36).slice(2)}`,
      payload,
      status: 'pending',
      attempts: 0,
      maxAttempts: this.config?.maxRetryAttempts ?? RETRY_CONFIG.MAX_ATTEMPTS,
      createdAt: new Date().toISOString(),
      scheduledAt: new Date().toISOString(),
      lastAttemptAt: null,
      completedAt: null,
      nextRetryAt: null,
      lastError: null,
      priority: 0,
    }

    let existing = await this.getAll()
    
    // Enforce max queue size by dropping oldest pending items if needed
    const maxSize = this.config?.maxQueueSize ?? 100
    if (existing.length >= maxSize) {
      logger.warn('Queue full, dropping oldest items', { maxSize })
      existing = existing.sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()).slice(existing.length - maxSize + 1)
    }

    existing.push(item)
    await this.persist(existing)
    logger.info('Item enqueued', { id: item.id })
    return item
  }

  async getAll(): Promise<QueueItem[]> {
    const result = await chrome.storage.local.get(STORAGE_KEYS.QUEUE_ITEMS)
    return (result[STORAGE_KEYS.QUEUE_ITEMS] as QueueItem[]) ?? []
  }

  async getPending(): Promise<QueueItem[]> {
    const all = await this.getAll()
    return all.filter((item) => item.status === 'pending')
  }

  async updateStatus(id: string, status: QueueItemStatus): Promise<void> {
    const all = await this.getAll()
    const updated = all.map((item) =>
      item.id === id ? { ...item, status, lastAttemptAt: new Date().toISOString() } : item
    )
    await this.persist(updated)
  }

  async remove(id: string): Promise<void> {
    const all = await this.getAll()
    await this.persist(all.filter((item) => item.id !== id))
    logger.info('Item removed from queue', { id })
  }

  async processQueue(): Promise<void> {
    const pending = await this.getPending()
    if (pending.length === 0) return

    logger.info('Processing queue batch', { count: pending.length })

    // PHASE 3: Upload to backend
    for (const item of pending) {
      await this.updateStatus(item.id, 'processing')
      
      try {
        const response = await fetch('http://localhost:8000/api/v1/extension/ingest', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(item.payload)
        })

        if (!response.ok) {
          throw new Error(`Upload failed with status ${response.status}`)
        }
        
        logger.info('Upload successful for payload', { id: item.id })
        await this.remove(item.id)
      } catch (error) {
        logger.error('Failed to upload payload, will retry later', error)
        // Set back to pending or failed if max attempts reached.
        // For simplicity, we just leave it pending to retry next cycle.
        await this.updateStatus(item.id, 'pending')
      }
    }
  }

  async getStats(): Promise<QueueStats> {
    const all = await this.getAll()
    const byStatus = (s: QueueItemStatus) => all.filter((i) => i.status === s).length
    const pending = all.filter((i) => i.status === 'pending')

    return {
      totalItems: all.length,
      pendingItems: byStatus('pending'),
      processingItems: byStatus('processing'),
      completedItems: byStatus('completed'),
      failedItems: byStatus('failed'),
      deadLetterItems: byStatus('dead_letter'),
      oldestPendingAt: pending.length > 0 ? (pending[0]?.createdAt ?? null) : null,
    }
  }

  private async persist(items: QueueItem[]): Promise<void> {
    await chrome.storage.local.set({ [STORAGE_KEYS.QUEUE_ITEMS]: items })
  }
}

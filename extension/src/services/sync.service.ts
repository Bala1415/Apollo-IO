import { createLogger } from '@/logger'
import { LocalStorageService } from '@/storage'
import { STORAGE_KEYS } from '@/config'

const logger = createLogger('SyncService')
const storage = new LocalStorageService()

export class SyncService {
  async getLastSyncAt(): Promise<string | null> {
    return storage.get<string>(STORAGE_KEYS.LAST_SYNC_AT)
  }

  async markSyncComplete(): Promise<void> {
    const now = new Date().toISOString()
    await storage.set(STORAGE_KEYS.LAST_SYNC_AT, now)
    logger.info('Sync marked complete', { at: now })
  }

  async triggerSync(): Promise<void> {
    logger.info('SyncService.triggerSync — implementation pending')
  }
}

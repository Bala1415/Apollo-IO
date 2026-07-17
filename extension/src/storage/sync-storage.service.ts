import type { IStorageService } from './interfaces/storage.interface'
import { createLogger } from '@/logger'

const logger = createLogger('SyncStorageService')

export class SyncStorageService implements IStorageService {
  async get<T>(key: string): Promise<T | null> {
    const result = await chrome.storage.sync.get(key)
    return (result[key] as T) ?? null
  }

  async set<T>(key: string, value: T): Promise<void> {
    await chrome.storage.sync.set({ [key]: value })
    logger.debug('Sync storage set', { key })
  }

  async remove(key: string): Promise<void> {
    await chrome.storage.sync.remove(key)
  }

  async clear(): Promise<void> {
    await chrome.storage.sync.clear()
    logger.warn('Sync storage cleared')
  }

  async keys(): Promise<string[]> {
    const all = await chrome.storage.sync.get(null)
    return Object.keys(all)
  }
}

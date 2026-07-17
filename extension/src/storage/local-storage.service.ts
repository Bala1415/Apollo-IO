import type { IStorageService } from './interfaces/storage.interface'
import { createLogger } from '@/logger'

const logger = createLogger('LocalStorageService')

export class LocalStorageService implements IStorageService {
  async get<T>(key: string): Promise<T | null> {
    const result = await chrome.storage.local.get(key)
    return (result[key] as T) ?? null
  }

  async set<T>(key: string, value: T): Promise<void> {
    await chrome.storage.local.set({ [key]: value })
    logger.debug('Local storage set', { key })
  }

  async remove(key: string): Promise<void> {
    await chrome.storage.local.remove(key)
    logger.debug('Local storage removed', { key })
  }

  async clear(): Promise<void> {
    await chrome.storage.local.clear()
    logger.warn('Local storage cleared')
  }

  async keys(): Promise<string[]> {
    const all = await chrome.storage.local.get(null)
    return Object.keys(all)
  }
}

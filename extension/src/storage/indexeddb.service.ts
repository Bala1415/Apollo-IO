import type { IIndexedDBService } from './interfaces/storage.interface'
import { createLogger } from '@/logger'

const logger = createLogger('IndexedDBService')

const DB_NAME = 'ai_browser_intelligence'
const DB_VERSION = 1
export const STORE_NAMES = {
  QUEUE: 'queue_items',
  SIGNALS: 'signals',
  SESSIONS: 'sessions',
  LOGS: 'logs',
} as const

export class IndexedDBService implements IIndexedDBService {
  private db: IDBDatabase | null = null

  async open(_storeName: string): Promise<void> {
    if (this.db) return

    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION)

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result
        for (const store of Object.values(STORE_NAMES)) {
          if (!db.objectStoreNames.contains(store)) {
            db.createObjectStore(store, { keyPath: 'id' })
            logger.info('Object store created', { store })
          }
        }
      }

      request.onsuccess = (event) => {
        this.db = (event.target as IDBOpenDBRequest).result
        logger.info('IndexedDB opened', { name: DB_NAME, version: DB_VERSION })
        resolve()
      }

      request.onerror = (event) => {
        reject(new Error(`IndexedDB open failed: ${(event.target as IDBOpenDBRequest).error?.message}`))
      }
    })
  }

  async getItem<T>(storeName: string, key: string): Promise<T | null> {
    await this.open(storeName)
    const db = this.db
    if (!db) return null

    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readonly')
      const store = tx.objectStore(storeName)
      const request = store.get(key)
      request.onsuccess = () => resolve((request.result as T) ?? null)
      request.onerror = () => reject(request.error)
    })
  }

  async setItem<T>(storeName: string, _key: string, value: T): Promise<void> {
    await this.open(storeName)
    const db = this.db
    if (!db) return

    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readwrite')
      const store = tx.objectStore(storeName)
      const request = store.put(value)
      request.onsuccess = () => resolve()
      request.onerror = () => reject(request.error)
    })
  }

  async deleteItem(storeName: string, key: string): Promise<void> {
    await this.open(storeName)
    const db = this.db
    if (!db) return

    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readwrite')
      const store = tx.objectStore(storeName)
      const request = store.delete(key)
      request.onsuccess = () => resolve()
      request.onerror = () => reject(request.error)
    })
  }

  async getAllItems<T>(storeName: string): Promise<T[]> {
    await this.open(storeName)
    const db = this.db
    if (!db) return []

    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readonly')
      const store = tx.objectStore(storeName)
      const request = store.getAll()
      request.onsuccess = () => resolve(request.result as T[])
      request.onerror = () => reject(request.error)
    })
  }

  async clear(storeName: string): Promise<void> {
    await this.open(storeName)
    const db = this.db
    if (!db) return

    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readwrite')
      const store = tx.objectStore(storeName)
      const request = store.clear()
      request.onsuccess = () => resolve()
      request.onerror = () => reject(request.error)
    })
  }
}

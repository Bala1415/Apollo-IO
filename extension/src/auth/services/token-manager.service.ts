import type { ITokenManager } from '../interfaces/auth.interface'
import { STORAGE_KEYS } from '@/config'
import { createLogger } from '@/logger'

const logger = createLogger('TokenManager')

export class TokenManager implements ITokenManager {
  async storeToken(token: string, expiresAt: number): Promise<void> {
    logger.debug('Storing auth token')
    await chrome.storage.local.set({
      [STORAGE_KEYS.AUTH_TOKEN]: token,
      [`${STORAGE_KEYS.AUTH_TOKEN}_expires`]: expiresAt,
    })
  }

  async getToken(): Promise<string | null> {
    const result = await chrome.storage.local.get(STORAGE_KEYS.AUTH_TOKEN)
    return (result[STORAGE_KEYS.AUTH_TOKEN] as string) ?? null
  }

  async getExpiresAt(): Promise<number | null> {
    const result = await chrome.storage.local.get(`${STORAGE_KEYS.AUTH_TOKEN}_expires`)
    return (result[`${STORAGE_KEYS.AUTH_TOKEN}_expires`] as number) ?? null
  }

  async clearToken(): Promise<void> {
    logger.debug('Clearing auth token')
    await chrome.storage.local.remove([
      STORAGE_KEYS.AUTH_TOKEN,
      `${STORAGE_KEYS.AUTH_TOKEN}_expires`,
    ])
  }

  async isExpired(): Promise<boolean> {
    const expiresAt = await this.getExpiresAt()
    if (!expiresAt) return true
    return Date.now() >= expiresAt
  }
}

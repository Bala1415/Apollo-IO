import type { ISessionManager } from '../interfaces/auth.interface'
import { STORAGE_KEYS } from '@/config'
import { createLogger } from '@/logger'

const logger = createLogger('SessionManager')

export class SessionManager implements ISessionManager {
  async createSession(userId: string): Promise<string> {
    const sessionId = `session_${userId}_${Date.now()}`
    logger.info('Creating session', { sessionId })
    await chrome.storage.local.set({ [STORAGE_KEYS.SESSION_ID]: sessionId })
    return sessionId
  }

  async endSession(sessionId: string): Promise<void> {
    logger.info('Ending session', { sessionId })
    const current = await this.getCurrentSessionId()
    if (current === sessionId) {
      await chrome.storage.local.remove(STORAGE_KEYS.SESSION_ID)
    }
  }

  async getCurrentSessionId(): Promise<string | null> {
    const result = await chrome.storage.local.get(STORAGE_KEYS.SESSION_ID)
    return (result[STORAGE_KEYS.SESSION_ID] as string) ?? null
  }

  async getSessionDuration(_sessionId: string): Promise<number> {
    return 0
  }
}

import type { IAuthService, GoogleOAuthResult, TokenRefreshResult } from '../interfaces/auth.interface'
import type { User } from '@ai-browser-intelligence/shared-types'
import { createLogger } from '@/logger'
import { TokenManager } from './token-manager.service'

const logger = createLogger('GoogleOAuthService')

export class GoogleOAuthService implements IAuthService {
  private readonly tokenManager = new TokenManager()

  async signIn(): Promise<GoogleOAuthResult> {
    logger.info('Initiating Google OAuth sign-in')
    return new Promise((resolve, reject) => {
      chrome.identity.getAuthToken({ interactive: true }, async (token) => {
        if (chrome.runtime.lastError || !token) {
          logger.error('OAuth sign-in failed', chrome.runtime.lastError)
          return reject(new Error(chrome.runtime.lastError?.message ?? 'OAuth failed'))
        }

        try {
          // Fetch user profile from Google
          const response = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
            headers: { Authorization: `Bearer ${token}` }
          })
          if (!response.ok) throw new Error('Failed to fetch user profile')
          
          const profile = await response.json()
          
          const user: User = {
            id: profile.id,
            googleId: profile.id,
            email: profile.email,
            displayName: profile.name,
            avatarUrl: profile.picture,
            role: 'user',
            status: 'active',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          }

          // Google tokens usually expire in 1 hour (3600 seconds)
          const expiresAt = Date.now() + 3600 * 1000
          await this.tokenManager.storeToken(token, expiresAt)
          
          resolve({ token, expiresAt, user })
        } catch (error) {
          logger.error('Failed to process OAuth result', error)
          reject(error)
        }
      })
    })
  }

  async signOut(): Promise<void> {
    logger.info('Signing out')
    const token = await this.tokenManager.getToken()
    if (token) {
      return new Promise<void>((resolve) => {
        chrome.identity.removeCachedAuthToken({ token }, async () => {
          await this.tokenManager.clearToken()
          resolve()
        })
      })
    }
    await this.tokenManager.clearToken()
  }

  async refreshToken(): Promise<TokenRefreshResult> {
    logger.info('Refreshing auth token')
    // Remove the cached token first to force a refresh
    const oldToken = await this.tokenManager.getToken()
    if (oldToken) {
      await new Promise<void>((resolve) => chrome.identity.removeCachedAuthToken({ token: oldToken }, resolve))
    }

    return new Promise((resolve, reject) => {
      chrome.identity.getAuthToken({ interactive: false }, async (token) => {
        if (chrome.runtime.lastError || !token) {
          logger.error('Token refresh failed', chrome.runtime.lastError)
          return reject(new Error(chrome.runtime.lastError?.message ?? 'Refresh failed'))
        }
        const expiresAt = Date.now() + 3600 * 1000
        await this.tokenManager.storeToken(token, expiresAt)
        resolve({ token, expiresAt })
      })
    })
  }

  async getUserProfile(): Promise<any> {
    const token = await this.getToken()
    if (!token) return null
    try {
      const response = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (!response.ok) return null
      return await response.json()
    } catch {
      return null
    }
  }

  async getToken(): Promise<string | null> {
    return this.tokenManager.getToken()
  }

  async isTokenValid(): Promise<boolean> {
    const expired = await this.tokenManager.isExpired()
    return !expired
  }
}

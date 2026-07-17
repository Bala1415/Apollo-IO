import type { User, UserProfile } from '@ai-browser-intelligence/shared-types'

export interface AuthState {
  readonly isAuthenticated: boolean
  readonly user: User | null
  readonly profile: UserProfile | null
  readonly token: string | null
  readonly expiresAt: number | null
  readonly isLoading: boolean
  readonly error: AuthError | null
}

export interface AuthError {
  readonly code: AuthErrorCode
  readonly message: string
}

export type AuthErrorCode =
  | 'OAUTH_FAILED'
  | 'TOKEN_EXPIRED'
  | 'TOKEN_INVALID'
  | 'NETWORK_ERROR'
  | 'USER_CANCELLED'
  | 'PERMISSION_DENIED'

export interface GoogleOAuthResult {
  readonly token: string
  readonly expiresAt: number
  readonly user: User
}

export interface TokenRefreshResult {
  readonly token: string
  readonly expiresAt: number
}

export interface IAuthService {
  signIn(): Promise<GoogleOAuthResult>
  signOut(): Promise<void>
  refreshToken(): Promise<TokenRefreshResult>
  getToken(): Promise<string | null>
  isTokenValid(): Promise<boolean>
}

export interface ITokenManager {
  storeToken(token: string, expiresAt: number): Promise<void>
  getToken(): Promise<string | null>
  getExpiresAt(): Promise<number | null>
  clearToken(): Promise<void>
  isExpired(): Promise<boolean>
}

export interface ISessionManager {
  createSession(userId: string): Promise<string>
  endSession(sessionId: string): Promise<void>
  getCurrentSessionId(): Promise<string | null>
  getSessionDuration(sessionId: string): Promise<number>
}

export type {
  AuthState,
  AuthError,
  AuthErrorCode,
  GoogleOAuthResult,
  TokenRefreshResult,
  IAuthService,
  ITokenManager,
  ISessionManager,
} from './interfaces/auth.interface'

export { GoogleOAuthService } from './services/google-oauth.service'
export { TokenManager } from './services/token-manager.service'
export { SessionManager } from './services/session-manager.service'
export { AuthProvider, useAuthContext } from './context/auth.context'

import { createLogger } from '@/logger'

const logger = createLogger('Auth')

export async function initializeAuth(): Promise<void> {
  logger.info('Initializing authentication module')
}

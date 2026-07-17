import { useState, useCallback, useEffect } from 'react'
import { useAuthContext } from '@/auth'
import type { AuthError } from '@/auth'
import { sendMessageToBackground } from '@/services/messaging.service'
import { MESSAGE_TYPES } from '@/config'

interface UseAuthReturn {
  isAuthenticated: boolean
  user: ReturnType<typeof useAuthContext>['state']['user']
  isLoading: boolean
  error: AuthError | null
  signIn: () => Promise<void>
  signOut: () => Promise<void>
}

export function useAuth(): UseAuthReturn {
  const { state, dispatch } = useAuthContext()
  const [isSigningIn, setIsSigningIn] = useState(false)

  // Fetch initial state
  useEffect(() => {
    sendMessageToBackground<{ success: boolean; isAuthenticated?: boolean }>(MESSAGE_TYPES.AUTH_GET_STATE)
      .then((res) => {
        if (res.success && res.isAuthenticated) {
          // Ideally fetch user profile here if we wanted to fully sync state,
          // but for now we just rely on login action to populate context.
        }
      })
      .catch(() => {})
  }, [])

  const signIn = useCallback(async () => {
    setIsSigningIn(true)
    dispatch({ type: 'SET_LOADING', payload: true })
    try {
      const result = await sendMessageToBackground<{ success: boolean; data?: any; error?: string }>(MESSAGE_TYPES.AUTH_LOGIN)
      if (result.success && result.data) {
        dispatch({
          type: 'SET_AUTHENTICATED',
          payload: {
            user: result.data.user,
            token: result.data.token,
            expiresAt: result.data.expiresAt,
          } as any
        })
      } else {
        throw new Error(result.error || 'Login failed')
      }
    } catch (error) {
      dispatch({
        type: 'SET_ERROR',
        payload: { code: 'OAUTH_FAILED', message: String(error) },
      })
    } finally {
      setIsSigningIn(false)
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }, [dispatch])

  const signOut = useCallback(async () => {
    try {
      await sendMessageToBackground(MESSAGE_TYPES.AUTH_LOGOUT)
      dispatch({ type: 'SIGN_OUT' })
    } catch {
      dispatch({ type: 'SIGN_OUT' })
    }
  }, [dispatch])

  return {
    isAuthenticated: state.isAuthenticated,
    user: state.user,
    isLoading: state.isLoading || isSigningIn,
    error: state.error,
    signIn,
    signOut,
  }
}

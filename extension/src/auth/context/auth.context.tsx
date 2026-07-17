import React, { createContext, useContext, useReducer } from 'react'
import type { AuthState } from '../interfaces/auth.interface'

const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  profile: null,
  token: null,
  expiresAt: null,
  isLoading: false,
  error: null,
}

type AuthAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_AUTHENTICATED'; payload: Pick<AuthState, 'user' | 'profile' | 'token' | 'expiresAt'> }
  | { type: 'SET_ERROR'; payload: AuthState['error'] }
  | { type: 'SIGN_OUT' }

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload }
    case 'SET_AUTHENTICATED':
      return {
        ...state,
        isAuthenticated: true,
        isLoading: false,
        error: null,
        ...action.payload,
      }
    case 'SET_ERROR':
      return { ...state, isLoading: false, error: action.payload }
    case 'SIGN_OUT':
      return { ...initialState }
    default:
      return state
  }
}

interface AuthContextValue {
  state: AuthState
  dispatch: React.Dispatch<AuthAction>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState)
  return <AuthContext.Provider value={{ state, dispatch }}>{children}</AuthContext.Provider>
}

export function useAuthContext(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuthContext must be used within AuthProvider')
  return context
}

export type ChromeStorageArea = 'local' | 'sync' | 'session'

export interface ChromeMessage {
  type: string
  payload?: unknown
}

export interface ChromeMessageResponse<T = unknown> {
  success: boolean
  data?: T
  error?: string
}

export interface ExtensionStatus {
  isInitialized: boolean
  isAuthenticated: boolean
  allPermissionsGranted: boolean
  queuePending: number
  lastSyncAt: string | null
  version: string
}

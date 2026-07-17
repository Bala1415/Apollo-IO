export const EXTENSION_VERSION = '0.1.0'

export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_PROFILE: 'user_profile',
  DEVICE_ID: 'device_id',
  SESSION_ID: 'current_session_id',
  PERMISSION_STATE: 'permission_state',
  EXTENSION_CONFIG: 'extension_config',
  QUEUE_ITEMS: 'queue_items',
  LAST_SYNC_AT: 'last_sync_at',
  ONBOARDING_COMPLETE: 'onboarding_complete',
} as const

export const ALARM_NAMES = {
  SYNC_ALARM: 'ai_bi_sync',
  TOKEN_REFRESH_ALARM: 'ai_bi_token_refresh',
  QUEUE_FLUSH_ALARM: 'ai_bi_queue_flush',
} as const

export const MESSAGE_TYPES = {
  PING: 'PING',
  PONG: 'PONG',
  GET_STATUS: 'GET_STATUS',
  STATUS_RESPONSE: 'STATUS_RESPONSE',
  REQUEST_SYNC: 'REQUEST_SYNC',
  SYNC_COMPLETE: 'SYNC_COMPLETE',
  AUTH_STATE_CHANGED: 'AUTH_STATE_CHANGED',
  PERMISSION_CHANGED: 'PERMISSION_CHANGED',
  AUTH_LOGIN: 'AUTH_LOGIN',
  AUTH_LOGOUT: 'AUTH_LOGOUT',
  AUTH_GET_STATE: 'AUTH_GET_STATE',
  REQUEST_PERMISSION: 'REQUEST_PERMISSION',
  GET_PERMISSION_STATE: 'GET_PERMISSION_STATE',
} as const
export const API_ENDPOINTS = {
  HEALTH: '/health',
  BROWSER_PROFILE: '/api/v1/browser-profile',
  AUTH_VERIFY: '/api/v1/auth/verify',
} as const

export const RETRY_CONFIG = {
  MAX_ATTEMPTS: 5,
  BASE_DELAY_MS: 1000,
  MAX_DELAY_MS: 30000,
  BACKOFF_MULTIPLIER: 2,
  JITTER_ENABLED: true,
} as const

export const TIMING = {
  SYNC_INTERVAL_MS: 30 * 60 * 1000,
  TOKEN_REFRESH_BUFFER_MS: 5 * 60 * 1000,
  REQUEST_TIMEOUT_MS: 15000,
  IDLE_THRESHOLD_SECONDS: 300,
} as const

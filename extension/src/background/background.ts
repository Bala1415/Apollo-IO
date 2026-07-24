import type { LogLevel } from '@/logger'
import { createLogger } from '@/logger'
import { loadConfiguration, MESSAGE_TYPES, ALARM_NAMES, TIMING } from '@/config'
import { initializeAuth } from '@/auth'
import { GoogleOAuthService } from '@/auth/services/google-oauth.service'
import { initializePermissions, PermissionManager } from '@/permissions'
import { initializeCollectors } from '@/collectors'
import { initializeQueue } from '@/queue'
import { IntelligencePipeline } from '@/processors/intelligence.pipeline'

const logger = createLogger('Background')
const authService = new GoogleOAuthService()
const permissionManager = new PermissionManager()
const pipeline = new IntelligencePipeline()

async function initialize(): Promise<void> {
  try {
    logger.info('AI Browser Intelligence — initializing service worker')

    const config = await loadConfiguration()
    logger.info('Configuration loaded', { version: config.version, env: config.environment })

    await initializeAuth()
    logger.info('Auth module ready')

    await permissionManager.initialize()
    logger.info('Permission manager ready')

    if (config.featureFlags.historyCollectionEnabled || config.featureFlags.tabCollectionEnabled) {
      await initializeCollectors(config)
      logger.info('Collectors ready')
    }

    await initializeQueue(config)
    logger.info('Queue manager ready')

    // Setup periodic sync alarm for Local Intelligence Engine
    chrome.alarms.create(ALARM_NAMES.SYNC_ALARM, {
      periodInMinutes: Math.max(1, Math.round(TIMING.SYNC_INTERVAL_MS / 60000))
    })

    logger.info('Extension fully initialized')
  } catch (error) {
    logger.error('Initialization failed', error)
  }
}

chrome.runtime.onInstalled.addListener((details) => {
  logger.info('Extension installed/updated', {
    reason: details.reason,
    previousVersion: details.previousVersion,
  })
  void initialize()
})

chrome.runtime.onStartup.addListener(() => {
  logger.info('Browser startup detected')
  void initialize()
})

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === ALARM_NAMES.SYNC_ALARM) {
    logger.info('Sync alarm triggered, running intelligence pipeline')
    void pipeline.runPipeline()
  }
})

chrome.runtime.onMessage.addListener((message: unknown, sender: chrome.runtime.MessageSender, sendResponse: (response: unknown) => void) => {
  const msg = message as { type?: string; payload?: any }
  logger.debug('Message received', { type: msg?.type, from: sender.tab?.id })

  switch (msg?.type) {
    case MESSAGE_TYPES.PING:
      sendResponse({ received: true })
      break

    case MESSAGE_TYPES.AUTH_LOGIN:
      authService.signIn()
        .then((res) => {
          sendResponse({ success: true, data: res })
          // Force an immediate sync after login so the user doesn't wait 30 minutes
          void pipeline.runPipeline()
        })
        .catch((err) => sendResponse({ success: false, error: String(err) }))
      return true

    case MESSAGE_TYPES.AUTH_LOGOUT:
      authService.signOut()
        .then(() => sendResponse({ success: true }))
        .catch((err) => sendResponse({ success: false, error: String(err) }))
      return true

    case MESSAGE_TYPES.AUTH_GET_STATE:
      authService.getToken()
        .then((token) => sendResponse({ success: true, isAuthenticated: !!token }))
        .catch((err) => sendResponse({ success: false, error: String(err) }))
      return true

    case MESSAGE_TYPES.GET_PERMISSION_STATE:
      permissionManager.getPermissionState()
        .then((state) => sendResponse({ success: true, data: state }))
        .catch((err) => sendResponse({ success: false, error: String(err) }))
      return true

    case MESSAGE_TYPES.REQUEST_PERMISSION:
      permissionManager.requestPermissions(msg.payload?.permissions || [])
        .then((state) => sendResponse({ success: true, data: state }))
        .catch((err) => sendResponse({ success: false, error: String(err) }))
      return true

    default:
      sendResponse({ error: 'Unknown message type' })
      break
  }
  return false
})

void initialize()

export type { LogLevel }

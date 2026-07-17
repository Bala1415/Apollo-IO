import { MESSAGE_TYPES } from '@/config'
import { createLogger } from '@/logger'

const logger = createLogger('ContentScript')

function initialize(): void {
  logger.debug('Content script initialized', { url: window.location.hostname })
  registerMessageListeners()
}

function registerMessageListeners(): void {
  chrome.runtime.onMessage.addListener(
    (message: unknown, _sender: chrome.runtime.MessageSender, sendResponse: (response: unknown) => void) => {
      const msg = message as { type?: string }

      switch (msg?.type) {
        case MESSAGE_TYPES.PING:
          sendResponse({ type: MESSAGE_TYPES.PONG, timestamp: Date.now() })
          break
        default:
          break
      }

      return true
    }
  )
}

initialize()

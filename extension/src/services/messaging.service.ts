import { MESSAGE_TYPES } from '@/config'
import { createLogger } from '@/logger'

const logger = createLogger('MessagingService')

export function sendMessageToBackground<T>(
  type: string,
  payload?: unknown
): Promise<T> {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage({ type, payload }, (response: T) => {
      if (chrome.runtime.lastError) {
        reject(chrome.runtime.lastError)
        return
      }
      resolve(response)
    })
  })
}

export async function pingBackground(): Promise<boolean> {
  try {
    await sendMessageToBackground(MESSAGE_TYPES.PING)
    return true
  } catch {
    logger.warn('Background ping failed')
    return false
  }
}

export function broadcastToAllTabs(type: string, payload?: unknown): Promise<void[]> {
  return chrome.tabs.query({}).then((tabs) =>
    Promise.all(
      tabs
        .filter((tab) => tab.id !== undefined)
        .map((tab) =>
          chrome.tabs
            .sendMessage(tab.id!, { type, payload })
            .catch(() => undefined)
        )
    )
  )
}

export function onBackgroundMessage(
  handler: (message: { type: string; payload?: unknown }) => void
): void {
  chrome.runtime.onMessage.addListener((message: unknown) => {
    if (message && typeof message === 'object' && 'type' in message) {
      handler(message as { type: string; payload?: unknown })
    }
  })
}

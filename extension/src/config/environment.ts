import type { ExtensionConfiguration } from '@ai-browser-intelligence/shared-types'

export const DEFAULT_CONFIGURATION: ExtensionConfiguration = {
  version: '0.1.0',
  environment: (import.meta.env['VITE_ENV'] as ExtensionConfiguration['environment']) ?? 'development',
  apiBaseUrl: import.meta.env['VITE_API_BASE_URL'] ?? 'http://localhost:3001',
  apiVersion: 'v1',
  syncIntervalMinutes: 30,
  historyLookbackDays: 7,
  maxQueueSize: 100,
  maxRetryAttempts: 5,
  retryBackoffBaseMs: 1000,
  compressionEnabled: true,
  debugLoggingEnabled: import.meta.env['VITE_ENV'] === 'development',
  featureFlags: {
    historyCollectionEnabled: true,
    tabCollectionEnabled: true,
    sessionTrackingEnabled: true,
    searchCollectionEnabled: true,
    payloadCompressionEnabled: true,
    offlineQueueEnabled: true,
    detailedLoggingEnabled: import.meta.env['VITE_ENV'] === 'development',
  },
}

export async function loadConfiguration(): Promise<ExtensionConfiguration> {
  try {
    const stored = await chrome.storage.sync.get('extension_config')
    const overrides = stored['extension_config'] as Partial<ExtensionConfiguration> | undefined
    if (overrides) {
      return { ...DEFAULT_CONFIGURATION, ...overrides }
    }
  } catch {
    // Use default if storage unavailable
  }
  return DEFAULT_CONFIGURATION
}

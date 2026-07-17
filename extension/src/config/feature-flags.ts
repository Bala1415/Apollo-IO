import type { FeatureFlags } from '@ai-browser-intelligence/shared-types'

export const FEATURE_FLAGS: FeatureFlags = {
  historyCollectionEnabled: true,
  tabCollectionEnabled: true,
  sessionTrackingEnabled: true,
  searchCollectionEnabled: true,
  payloadCompressionEnabled: true,
  offlineQueueEnabled: true,
  detailedLoggingEnabled: import.meta.env['VITE_ENV'] === 'development',
}

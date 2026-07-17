import type { PermissionName } from '@ai-browser-intelligence/shared-types'

export interface PermissionConfig {
  readonly name: PermissionName
  readonly isRequired: boolean
  readonly description: string
  readonly reason: string
}

export const PERMISSION_CONFIGS: Record<PermissionName, PermissionConfig> = {
  history: {
    name: 'history',
    isRequired: true,
    description: 'Access browsing history',
    reason: 'Required to analyse browsing patterns and generate intelligence signals locally.',
  },
  tabs: {
    name: 'tabs',
    isRequired: true,
    description: 'Access active tab information',
    reason: 'Required to track active browsing sessions and detect domain categories.',
  },
  storage: {
    name: 'storage',
    isRequired: true,
    description: 'Store extension data',
    reason: 'Required to persist configuration, queue items, and session state locally.',
  },
  identity: {
    name: 'identity',
    isRequired: true,
    description: 'Google OAuth authentication',
    reason: 'Required to securely authenticate users via Google OAuth 2.0.',
  },
  alarms: {
    name: 'alarms',
    isRequired: true,
    description: 'Schedule background sync',
    reason: 'Required to schedule periodic data sync in the background service worker.',
  },
  notifications: {
    name: 'notifications',
    isRequired: false,
    description: 'Show notifications',
    reason: 'Optional — used to notify users about sync status and important events.',
  },
  background: {
    name: 'background',
    isRequired: true,
    description: 'Run in background',
    reason: 'Required for the service worker to operate when the browser is idle.',
  },
  scripting: {
    name: 'scripting',
    isRequired: false,
    description: 'Inject content scripts',
    reason: 'Optional — used for advanced page-level signal collection if enabled.',
  },
}

export const REQUIRED_PERMISSIONS: PermissionName[] = Object.values(PERMISSION_CONFIGS)
  .filter((p) => p.isRequired)
  .map((p) => p.name)

export const OPTIONAL_PERMISSIONS: PermissionName[] = Object.values(PERMISSION_CONFIGS)
  .filter((p) => !p.isRequired)
  .map((p) => p.name)

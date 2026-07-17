import type {
  PermissionName,
  PermissionState,
  PermissionStatus,
  Permission,
} from '@ai-browser-intelligence/shared-types'
import type { IPermissionManager } from './interfaces/permission.interface'
import { PERMISSION_CONFIGS, REQUIRED_PERMISSIONS } from '@/config'
import { createLogger } from '@/logger'

const logger = createLogger('PermissionManager')

export class PermissionManager implements IPermissionManager {
  async initialize(): Promise<void> {
    logger.info('Permission manager initializing')
    const state = await this.getPermissionState()
    logger.info('Current permission state', { allRequired: state.allRequiredGranted })
  }

  async getPermissionState(): Promise<PermissionState> {
    const permissions: Partial<Record<PermissionName, Permission>> = {}

    for (const name of Object.keys(PERMISSION_CONFIGS) as PermissionName[]) {
      const status = await this.checkPermission(name)
      const config = PERMISSION_CONFIGS[name]
      permissions[name] = {
        name,
        status,
        grantedAt: status === 'granted' ? new Date().toISOString() : null,
        deniedAt: status === 'denied' ? new Date().toISOString() : null,
        isRequired: config.isRequired,
        description: config.description,
      }
    }

    const allRequiredGranted = REQUIRED_PERMISSIONS.every(
      (name) => permissions[name]?.status === 'granted'
    )

    return {
      userId: '',
      permissions: permissions as Record<PermissionName, Permission>,
      allRequiredGranted,
      lastCheckedAt: new Date().toISOString(),
    }
  }

  async checkPermission(name: PermissionName): Promise<PermissionStatus> {
    try {
      const has = await chrome.permissions.contains({ permissions: [name] })
      return has ? 'granted' : 'not_requested'
    } catch {
      logger.warn('Failed to check permission', { name })
      return 'not_requested'
    }
  }

  async requestPermission(name: PermissionName): Promise<PermissionStatus> {
    logger.info('Requesting permission', { name })
    try {
      const granted = await chrome.permissions.request({ permissions: [name] })
      return granted ? 'granted' : 'denied'
    } catch {
      logger.error('Permission request failed', undefined, { name })
      return 'denied'
    }
  }

  async requestPermissions(names: PermissionName[]): Promise<PermissionState> {
    logger.info('Requesting multiple permissions', { names })
    for (const name of names) {
      await this.requestPermission(name)
    }
    return this.getPermissionState()
  }

  async revokePermission(name: PermissionName): Promise<void> {
    logger.info('Revoking permission', { name })
    await chrome.permissions.remove({ permissions: [name] })
  }
}

import type { PermissionName } from '@ai-browser-intelligence/shared-types'
import type { IPermissionService } from './interfaces/permission.interface'
import { REQUIRED_PERMISSIONS } from '@/config'
import { PermissionManager } from './permission-manager'

export class PermissionService implements IPermissionService {
  private readonly manager: PermissionManager

  constructor(manager: PermissionManager) {
    this.manager = manager
  }

  async hasPermission(name: PermissionName): Promise<boolean> {
    const status = await this.manager.checkPermission(name)
    return status === 'granted'
  }

  async hasAllRequired(): Promise<boolean> {
    const results = await Promise.all(
      REQUIRED_PERMISSIONS.map((name) => this.hasPermission(name))
    )
    return results.every(Boolean)
  }

  async getMissingRequired(): Promise<PermissionName[]> {
    const missing: PermissionName[] = []
    for (const name of REQUIRED_PERMISSIONS) {
      const has = await this.hasPermission(name)
      if (!has) missing.push(name)
    }
    return missing
  }
}

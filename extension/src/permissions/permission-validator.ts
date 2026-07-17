import type { PermissionName } from '@ai-browser-intelligence/shared-types'
import type { IPermissionValidator } from './interfaces/permission.interface'
import { PERMISSION_CONFIGS, REQUIRED_PERMISSIONS } from '@/config'

export class PermissionValidator implements IPermissionValidator {
  private readonly validNames: Set<PermissionName>

  constructor() {
    this.validNames = new Set(Object.keys(PERMISSION_CONFIGS) as PermissionName[])
  }

  validate(name: PermissionName): boolean {
    return this.validNames.has(name)
  }

  validateAll(names: PermissionName[]): boolean {
    return names.every((name) => this.validate(name))
  }

  isRequired(name: PermissionName): boolean {
    return REQUIRED_PERMISSIONS.includes(name)
  }
}

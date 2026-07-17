import type { PermissionName, PermissionState, PermissionStatus } from '@ai-browser-intelligence/shared-types'

export interface IPermissionManager {
  initialize(): Promise<void>
  getPermissionState(): Promise<PermissionState>
  checkPermission(name: PermissionName): Promise<PermissionStatus>
  requestPermission(name: PermissionName): Promise<PermissionStatus>
  requestPermissions(names: PermissionName[]): Promise<PermissionState>
  revokePermission(name: PermissionName): Promise<void>
}

export interface IPermissionService {
  hasPermission(name: PermissionName): Promise<boolean>
  hasAllRequired(): Promise<boolean>
  getMissingRequired(): Promise<PermissionName[]>
}

export interface IPermissionValidator {
  validate(name: PermissionName): boolean
  validateAll(names: PermissionName[]): boolean
  isRequired(name: PermissionName): boolean
}

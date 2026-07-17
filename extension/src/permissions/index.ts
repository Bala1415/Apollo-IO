export type {
  IPermissionManager,
  IPermissionService,
  IPermissionValidator,
} from './interfaces/permission.interface'

export { PermissionManager } from './permission-manager'
export { PermissionService } from './permission-service'
export { PermissionValidator } from './permission-validator'

import { PermissionManager } from './permission-manager'
import { createLogger } from '@/logger'

const logger = createLogger('Permissions')

export async function initializePermissions(): Promise<void> {
  logger.info('Initializing permission manager')
  const manager = new PermissionManager()
  await manager.initialize()
}

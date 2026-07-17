export type { Logger, LogLevel, LogEntry } from './interfaces/logger.interface'
export { ConsoleLogger } from './console.logger'
export { FileLogger } from './file.logger'

import { ConsoleLogger } from './console.logger'
import type { Logger } from './interfaces/logger.interface'

const loggerCache = new Map<string, Logger>()

export function createLogger(namespace: string): Logger {
  const cached = loggerCache.get(namespace)
  if (cached) return cached
  const logger = new ConsoleLogger(namespace)
  loggerCache.set(namespace, logger)
  return logger
}

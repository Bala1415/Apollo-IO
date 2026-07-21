import type { Logger } from './interfaces/logger.interface'

/**
 * FileLogger - Placeholder for future persistent log storage via IndexedDB.
 * In production, logs will be stored locally for debugging and error reporting.
 */
export class FileLogger implements Logger {
  private readonly namespace: string

  constructor(namespace: string) {
    this.namespace = namespace
  }

  debug(message: string, context?: Record<string, unknown>): void {
    console.debug(`[${this.namespace}] ${message}`, context || '')
  }

  info(message: string, context?: Record<string, unknown>): void {
    console.info(`[${this.namespace}] ${message}`, context || '')
  }

  warn(message: string, context?: Record<string, unknown>): void {
    console.warn(`[${this.namespace}] ${message}`, context || '')
  }

  error(message: string, error?: unknown, context?: Record<string, unknown>): void {
    console.error(`[${this.namespace}] ${message}`, error || '', context || '')
  }

  getNamespace(): string {
    return this.namespace
  }
}

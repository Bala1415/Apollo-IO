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

  debug(_message: string, _context?: Record<string, unknown>): void {
    // Future: persist to IndexedDB log store
  }

  info(_message: string, _context?: Record<string, unknown>): void {
    // Future: persist to IndexedDB log store
  }

  warn(_message: string, _context?: Record<string, unknown>): void {
    // Future: persist to IndexedDB log store
  }

  error(_message: string, _error?: unknown, _context?: Record<string, unknown>): void {
    // Future: persist to IndexedDB log store with error serialization
  }

  getNamespace(): string {
    return this.namespace
  }
}

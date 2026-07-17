export type LogLevel = 'debug' | 'info' | 'warn' | 'error'

export interface Logger {
  debug(message: string, context?: Record<string, unknown>): void
  info(message: string, context?: Record<string, unknown>): void
  warn(message: string, context?: Record<string, unknown>): void
  error(message: string, error?: unknown, context?: Record<string, unknown>): void
}

export interface LogEntry {
  readonly level: LogLevel
  readonly message: string
  readonly context?: Record<string, unknown>
  readonly timestamp: string
  readonly namespace: string
}

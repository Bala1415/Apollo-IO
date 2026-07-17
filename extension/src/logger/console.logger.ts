import type { Logger, LogLevel } from './interfaces/logger.interface'

const LOG_LEVELS: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
}

const currentLevel: LogLevel = (import.meta.env['VITE_LOG_LEVEL'] as LogLevel) ?? 'info'

function shouldLog(level: LogLevel): boolean {
  return LOG_LEVELS[level] >= LOG_LEVELS[currentLevel]
}

function formatMessage(namespace: string, message: string): string {
  return `[AI-BI][${namespace}] ${message}`
}

export class ConsoleLogger implements Logger {
  private readonly namespace: string

  constructor(namespace: string) {
    this.namespace = namespace
  }

  debug(message: string, context?: Record<string, unknown>): void {
    if (!shouldLog('debug')) return
    // eslint-disable-next-line no-console
    console.debug(formatMessage(this.namespace, message), context ?? '')
  }

  info(message: string, context?: Record<string, unknown>): void {
    if (!shouldLog('info')) return
    // eslint-disable-next-line no-console
    console.info(formatMessage(this.namespace, message), context ?? '')
  }

  warn(message: string, context?: Record<string, unknown>): void {
    if (!shouldLog('warn')) return
    // eslint-disable-next-line no-console
    console.warn(formatMessage(this.namespace, message), context ?? '')
  }

  error(message: string, error?: unknown, context?: Record<string, unknown>): void {
    if (!shouldLog('error')) return
    // eslint-disable-next-line no-console
    console.error(formatMessage(this.namespace, message), error, context ?? '')
  }
}

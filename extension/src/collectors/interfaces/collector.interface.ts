import type { ExtensionConfiguration } from '@ai-browser-intelligence/shared-types'

export interface ICollector<T> {
  collect(config: ExtensionConfiguration): Promise<T>
  isAvailable(): Promise<boolean>
  reset(): void
}

export interface CollectorResult<T> {
  readonly collectorName: string
  readonly data: T
  readonly collectedAt: string
  readonly durationMs: number
  readonly success: boolean
  readonly error?: string
}

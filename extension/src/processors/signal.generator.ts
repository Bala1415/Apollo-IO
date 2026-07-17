import type { Signal, SignalBatch, ProcessedHistoryEntry } from '@ai-browser-intelligence/shared-types'
import { createLogger } from '@/logger'

const logger = createLogger('SignalGenerator')

export class SignalGenerator {
  generateSignals(
    entries: ProcessedHistoryEntry[],
    sessionId: string,
    userId: string
  ): SignalBatch {
    logger.info('SignalGenerator.generateSignals — implementation pending', {
      entryCount: entries.length,
    })

    const signals: Signal[] = []

    return {
      sessionId,
      userId,
      signals,
      totalCount: signals.length,
      periodStart: new Date().toISOString(),
      periodEnd: new Date().toISOString(),
    }
  }
}

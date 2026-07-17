import type { ProcessedHistoryEntry, Interest } from '@ai-browser-intelligence/shared-types'
import type { IInterestEngine } from './interfaces/processor.interface'
import { createLogger } from '@/logger'
import { getCategoryById } from '@ai-browser-intelligence/taxonomy'

const logger = createLogger('InterestEngine')

const MAX_SCORE = 100
const RECENCY_WEIGHT = 0.4
const FREQUENCY_WEIGHT = 0.6

export class InterestEngine implements IInterestEngine {
  async process(entries: ProcessedHistoryEntry[]): Promise<Interest[]> {
    return this.detectInterests(entries)
  }

  async detectInterests(entries: ProcessedHistoryEntry[]): Promise<Interest[]> {
    logger.info('Calculating interest scores', { entryCount: entries.length })

    const categoryStats = new Map<string, { count: number; lastVisited: number; duration: number }>()

    for (const entry of entries) {
      if (entry.categoryId === 'cat_unknown') continue

      const existing = categoryStats.get(entry.categoryId) || { count: 0, lastVisited: 0, duration: 0 }
      const visitTime = new Date(entry.lastVisitedAt).getTime()

      categoryStats.set(entry.categoryId, {
        count: existing.count + entry.visitCount,
        lastVisited: Math.max(existing.lastVisited, visitTime),
        duration: existing.duration + entry.timeSpentSeconds,
      })
    }

    const now = Date.now()
    const maxPossibleCount = Math.max(...Array.from(categoryStats.values()).map((s) => s.count), 1)

    const interests: Interest[] = []

    for (const [categoryId, stats] of categoryStats.entries()) {
      const category = getCategoryById(categoryId)
      if (!category) continue

      // Frequency score (0-100)
      const frequencyScore = (stats.count / maxPossibleCount) * 100

      // Recency score (0-100), decays over 30 days
      const daysSinceVisit = (now - stats.lastVisited) / (1000 * 60 * 60 * 24)
      const recencyScore = Math.max(0, 100 - (daysSinceVisit / 30) * 100)

      // Duration multiplier (max 1.2x)
      const durationMultiplier = Math.min(1.2, 1 + stats.duration / 3600) // Caps at 1 hour

      let rawScore = (frequencyScore * FREQUENCY_WEIGHT + recencyScore * RECENCY_WEIGHT) * durationMultiplier
      
      interests.push({
        id: crypto.randomUUID(),
        userId: 'local', // To be filled by payload builder if needed
        categoryId,
        subcategoryId: null,
        name: category.name,
        confidence: 'medium', // InterestConfidence
        confidenceScore: Math.min(Math.round(rawScore), MAX_SCORE),
        evidenceCount: stats.count,
        firstDetectedAt: new Date(stats.lastVisited).toISOString(),
        lastConfirmedAt: new Date().toISOString(),
        trendDirection: 'stable',
      })
    }

    return interests.sort((a, b) => b.confidenceScore - a.confidenceScore)
  }
}


import type { Interest } from '@ai-browser-intelligence/shared-types'
import { CATEGORY_IDS } from '@ai-browser-intelligence/taxonomy'

export interface BusinessIntentScores {
  overallBusinessIntent: number
  technologyIntent: number
  buyingIntent: number
  enterpriseIntent: number
  learningIntent: number
  decisionMakerConfidence: number
}

export class IntentEngine {
  calculateIntent(interests: Interest[]): BusinessIntentScores {
    let overallBusinessIntent = 0
    let technologyIntent = 0
    let buyingIntent = 0
    let enterpriseIntent = 0
    let learningIntent = 0
    let decisionMakerConfidence = 0

    const getScore = (id: string) => interests.find(i => i.categoryId === id)?.confidenceScore || 0

    // Business = Business + CRM + Enterprise + ERP + Project Management + Communication
    overallBusinessIntent = Math.min(100, (
      getScore(CATEGORY_IDS.BUSINESS) +
      getScore(CATEGORY_IDS.CRM) +
      getScore(CATEGORY_IDS.ENTERPRISE) +
      getScore(CATEGORY_IDS.ERP) +
      getScore(CATEGORY_IDS.PROJECT_MANAGEMENT) +
      getScore(CATEGORY_IDS.COMMUNICATION)
    ))

    // Tech = Tech + Cloud + AI + Data + DevOps + Database
    technologyIntent = Math.min(100, (
      getScore(CATEGORY_IDS.TECHNOLOGY) +
      getScore(CATEGORY_IDS.CLOUD) +
      getScore(CATEGORY_IDS.AI) +
      getScore(CATEGORY_IDS.DATA) +
      getScore(CATEGORY_IDS.DATABASE) +
      getScore(CATEGORY_IDS.DEVOPS) +
      getScore(CATEGORY_IDS.DEVELOPMENT)
    ))

    // Buying Intent = Research + Finance + Enterprise
    buyingIntent = Math.min(100, (
      getScore(CATEGORY_IDS.RESEARCH) * 0.5 +
      getScore(CATEGORY_IDS.FINANCE) * 0.5 +
      getScore(CATEGORY_IDS.ENTERPRISE) * 0.3
    ))

    // Enterprise = Enterprise + ERP + Cloud
    enterpriseIntent = Math.min(100, (
      getScore(CATEGORY_IDS.ENTERPRISE) +
      getScore(CATEGORY_IDS.ERP) +
      getScore(CATEGORY_IDS.CLOUD) * 0.5
    ))

    // Learning = Education + Research
    learningIntent = Math.min(100, (
      getScore(CATEGORY_IDS.EDUCATION) +
      getScore(CATEGORY_IDS.RESEARCH)
    ))

    // Decision Maker Confidence (Heuristic based on deep Enterprise/Cloud/ERP interest)
    if (enterpriseIntent > 50 || technologyIntent > 70) {
      decisionMakerConfidence = Math.min(100, (enterpriseIntent + technologyIntent) / 2)
    }

    return {
      overallBusinessIntent: Math.round(overallBusinessIntent),
      technologyIntent: Math.round(technologyIntent),
      buyingIntent: Math.round(buyingIntent),
      enterpriseIntent: Math.round(enterpriseIntent),
      learningIntent: Math.round(learningIntent),
      decisionMakerConfidence: Math.round(decisionMakerConfidence),
    }
  }
}

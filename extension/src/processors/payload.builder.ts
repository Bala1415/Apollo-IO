import type { BrowserPayload, PayloadUser, PayloadDevice, PayloadSession, PayloadBrowsingSummary, PayloadSignals } from '@ai-browser-intelligence/shared-types'
import type { ProcessedHistoryEntry, Interest } from '@ai-browser-intelligence/shared-types'
import type { BusinessIntentScores } from './intent.engine'
import type { CompanyIdentity } from './company.extractor'
import { EXTENSION_VERSION } from '@/config'

export class PayloadBuilder {
  build(params: {
    user: chrome.identity.UserInfo & { companyIdentity: CompanyIdentity }
    intentScores: BusinessIntentScores
    interests: Interest[]
    history: ProcessedHistoryEntry[]
    activeTab: chrome.tabs.Tab | null
    sessionDuration: number
  }): BrowserPayload {
    const { user, intentScores, interests, history, activeTab, sessionDuration } = params

    const payloadUser: PayloadUser = {
      googleId: user.id,
      email: user.email,
      companyDomain: user.companyIdentity.domain,
      displayName: user.companyIdentity.name || user.email.split('@')[0] || 'User',
    }

    const payloadDevice: PayloadDevice = {
      browser: 'chrome',
      extensionVersion: EXTENSION_VERSION,
      language: navigator.language,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    }

    const payloadSession: PayloadSession = {
      currentWebsite: activeTab?.url ? new URL(activeTab.url).hostname : null,
      pageTitle: activeTab?.title || null,
      sessionDuration,
    }

    const businessDomains = history.filter(h => h.isWorkRelated).length
    
    // Group top history counts
    const historySummary: Record<string, number> = {}
    history.slice(0, 20).forEach(h => {
      historySummary[h.domain] = h.visitCount
    })

    const payloadBrowsingSummary: PayloadBrowsingSummary = {
      visitedDomains: history.length,
      businessDomains,
      interestCategories: interests.slice(0, 5).map(i => i.categoryId),
      historySummary,
    }

    const payloadSignals: PayloadSignals = {
      crmIntent: intentScores.overallBusinessIntent, // Could be more specific if needed
      cloudIntent: intentScores.technologyIntent,
      aiIntent: intentScores.technologyIntent,
      overallBusinessIntent: intentScores.overallBusinessIntent,
      learningIntent: intentScores.learningIntent,
      buyingIntent: intentScores.buyingIntent,
    }

    return {
      id: crypto.randomUUID(),
      version: 'v1',
      timestamp: new Date().toISOString(),
      user: payloadUser,
      device: payloadDevice,
      currentSession: payloadSession,
      browsingSummary: payloadBrowsingSummary,
      signals: payloadSignals,
    }
  }
}

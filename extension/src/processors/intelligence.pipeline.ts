import { createLogger } from '@/logger'
import { HistoryCollector } from '@/collectors/history.collector'
import { TabsCollector } from '@/collectors/tabs.collector'
import { HistoryProcessor } from './history.processor'
import { InterestEngine } from './interest.engine'
import { IntentEngine } from './intent.engine'
import { CompanyExtractor } from './company.extractor'
import { PayloadBuilder } from './payload.builder'
import { QueueManager } from '@/queue/queue.manager'
import { GoogleOAuthService } from '@/auth/services/google-oauth.service'

const logger = createLogger('IntelligencePipeline')

export class IntelligencePipeline {
  private historyCollector = new HistoryCollector()
  private tabsCollector = new TabsCollector()
  private historyProcessor = new HistoryProcessor()
  private interestEngine = new InterestEngine()
  private intentEngine = new IntentEngine()
  private companyExtractor = new CompanyExtractor()
  private payloadBuilder = new PayloadBuilder()
  private queueManager = new QueueManager()
  private authService = new GoogleOAuthService()

  private config = {
    version: '0.1.0',
    environment: 'development' as const,
    logLevel: 'debug' as const,
    syncIntervalSeconds: 3600,
    maxQueueSize: 100,
    maxRetryAttempts: 3,
    apiBaseUrl: '',
    historyLookbackDays: 30,
    apiVersion: 'v1',
    syncIntervalMinutes: 60,
    retryBackoffBaseMs: 1000,
    compressionEnabled: true,
    debugLoggingEnabled: true,
    featureFlags: {
      historyCollectionEnabled: true,
      tabCollectionEnabled: true,
      sessionTrackingEnabled: true,
      searchCollectionEnabled: false,
      payloadCompressionEnabled: true,
      offlineQueueEnabled: true,
      detailedLoggingEnabled: true,
    },
  }

  constructor() {
    this.queueManager.initialize(this.config)
  }

  async runPipeline(): Promise<void> {
    try {
      logger.info('Starting Intelligence Pipeline')
      
      const [token, userProfile] = await Promise.all([
        this.authService.getToken(),
        this.authService.getUserProfile()
      ])

      if (!token || !userProfile) {
        logger.warn('Cannot run pipeline: User is not authenticated')
        return
      }

      // 1. Collect
      const rawHistory = await this.historyCollector.collect(this.config)
      const activeTabs = await this.tabsCollector.collect(this.config)
      const activeTab = activeTabs.length > 0 ? activeTabs[0] : null
      
      // 2. Process History
      const processedHistory = await this.historyProcessor.process(rawHistory)
      
      // 3. Process Interests
      const interests = await this.interestEngine.process(processedHistory)

      // 4. Calculate Intent
      const intentScores = this.intentEngine.calculateIntent(interests)

      // 5. Extract Company Info
      const companyIdentity = this.companyExtractor.extractIdentity(userProfile.email)

      // 6. Build Payload
      const payload = this.payloadBuilder.build({
        user: { ...userProfile, companyIdentity },
        intentScores,
        interests,
        history: processedHistory,
        activeTab: activeTab as any, // Cast to any as Tab interface might vary slightly
        sessionDuration: 0, // Mocked for now, will integrate with SessionCollector
      })

      // 7. Cache Payload internally
      await chrome.storage.local.set({
        latest_payload: payload,
        latest_intent_scores: intentScores,
        latest_interests: interests,
      })

      // 8. Queue for Upload
      await this.queueManager.enqueue(payload)
      
      // 9. Process Queue Batch
      await this.queueManager.processQueue()

      logger.info('Intelligence Pipeline completed successfully')

    } catch (error) {
      logger.error('Error running intelligence pipeline', error)
    }
  }
}

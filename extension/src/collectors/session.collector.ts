import type { ExtensionConfiguration, Session } from '@ai-browser-intelligence/shared-types'
import type { ICollector, CollectorResult } from './interfaces/collector.interface'
import { createLogger } from '@/logger'
import { extractDomain } from '@/utils'

const logger = createLogger('SessionCollector')

export class SessionCollector implements ICollector<Session[]> {
  private currentSession: Session | null = null
  private uniqueDomains = new Set<string>()

  constructor() {
    this.setupListeners()
    this.startNewSession()
  }

  private startNewSession() {
    this.currentSession = {
      id: crypto.randomUUID(),
      userId: 'anonymous', // Would be linked to actual user in Auth context
      deviceId: 'local',
      startedAt: new Date().toISOString(),
      endedAt: null,
      status: 'active',
      durationSeconds: 0,
      activeTabCount: 1,
      uniqueDomainsVisited: 0
    }
  }

  private setupListeners() {
    if (typeof chrome === 'undefined' || !chrome.tabs) return

    chrome.tabs.onActivated.addListener(this.handleTabChange.bind(this))
    chrome.tabs.onUpdated.addListener(this.handleTabUpdate.bind(this))
  }

  private async handleTabChange(activeInfo: chrome.tabs.TabActiveInfo) {
    if (!this.currentSession) return
    
    try {
      const tab = await chrome.tabs.get(activeInfo.tabId)
      if (tab.url) {
        const domain = extractDomain(tab.url)
        if (domain) {
          this.uniqueDomains.add(domain)
          this.updateSessionStats()
        }
      }
    } catch {
      // Tab might have been closed immediately
    }
  }

  private handleTabUpdate(_tabId: number, changeInfo: chrome.tabs.TabChangeInfo, tab: chrome.tabs.Tab) {
    if (!this.currentSession) return
    if (changeInfo.status === 'complete' && tab.url) {
      const domain = extractDomain(tab.url)
      if (domain) {
        this.uniqueDomains.add(domain)
        this.updateSessionStats()
      }
    }
  }

  private updateSessionStats() {
    if (!this.currentSession) return
    
    chrome.tabs.query({}, (tabs) => {
      if (!this.currentSession) return
      
      const durationMs = Date.now() - new Date(this.currentSession.startedAt).getTime()
      
      this.currentSession = {
        ...this.currentSession,
        activeTabCount: tabs.length,
        uniqueDomainsVisited: this.uniqueDomains.size,
        durationSeconds: Math.floor(durationMs / 1000)
      }
    })
  }

  async isAvailable(): Promise<boolean> {
    return true
  }

  reset(): void {
    logger.debug('SessionCollector reset')
    this.uniqueDomains.clear()
    this.startNewSession()
  }

  async collect(_config: ExtensionConfiguration): Promise<Session[]> {
    logger.debug('SessionCollector.collect called')
    this.updateSessionStats()
    return this.currentSession ? [this.currentSession] : []
  }

  async collectWithMeta(config: ExtensionConfiguration): Promise<CollectorResult<Session[]>> {
    const start = Date.now()
    try {
      const data = await this.collect(config)
      return {
        collectorName: 'SessionCollector',
        data,
        collectedAt: new Date().toISOString(),
        durationMs: Date.now() - start,
        success: true,
      }
    } catch (error) {
      return {
        collectorName: 'SessionCollector',
        data: [],
        collectedAt: new Date().toISOString(),
        durationMs: Date.now() - start,
        success: false,
        error: String(error),
      }
    }
  }
}

import type { IDomainExtractor } from './interfaces/processor.interface'
import type { DomainMetadata } from '@ai-browser-intelligence/shared-types'
import { createLogger } from '@/logger'

const logger = createLogger('DomainExtractor')

const INTERNAL_PATTERNS = ['chrome://', 'chrome-extension://', 'about:', 'moz-extension://']

export class DomainExtractor implements IDomainExtractor {
  extractDomain(url: string): string | null {
    try {
      const parsed = new URL(url)
      return parsed.hostname
    } catch {
      logger.debug('Failed to parse URL', { url: url.slice(0, 50) })
      return null
    }
  }

  extractHostname(url: string): string | null {
    try {
      const parsed = new URL(url)
      return parsed.hostname.replace(/^www\./, '')
    } catch {
      return null
    }
  }

  isInternalUrl(url: string): boolean {
    return INTERNAL_PATTERNS.some((pattern) => url.startsWith(pattern))
  }

  extractMetadata(url: string): DomainMetadata | null {
    try {
      const parsed = new URL(url)
      const hostParts = parsed.hostname.split('.')
      const tld = hostParts.slice(-2).join('.')
      const subdomain = hostParts.length > 2 ? hostParts.slice(0, -2).join('.') : null

      return {
        hostname: parsed.hostname,
        tld,
        subdomain: subdomain === 'www' ? null : subdomain,
        isSecure: parsed.protocol === 'https:',
      }
    } catch {
      return null
    }
  }
}

import type { ProcessedHistoryEntry, Interest } from '@ai-browser-intelligence/shared-types'
import type { RawHistoryEntry } from '@/collectors/history.collector'

export interface IProcessor<TInput, TOutput> {
  process(input: TInput): Promise<TOutput>
}

export interface IInterestEngine extends IProcessor<ProcessedHistoryEntry[], Interest[]> {
  detectInterests(entries: ProcessedHistoryEntry[]): Promise<Interest[]>
}

export interface ICategoryEngine {
  classify(domain: string): Promise<string>
  classifyBatch(domains: string[]): Promise<Map<string, string>>
}

export interface IDomainExtractor {
  extractDomain(url: string): string | null
  extractHostname(url: string): string | null
  isInternalUrl(url: string): boolean
}

export interface IHistoryProcessor extends IProcessor<RawHistoryEntry[], ProcessedHistoryEntry[]> {
  normalize(entries: RawHistoryEntry[]): Promise<ProcessedHistoryEntry[]>
  deduplicate(entries: ProcessedHistoryEntry[]): ProcessedHistoryEntry[]
  filter(entries: RawHistoryEntry[]): RawHistoryEntry[]
}

export function extractDomain(url: string): string | null {
  try {
    return new URL(url).hostname
  } catch {
    return null
  }
}

export function extractHostname(url: string): string | null {
  const domain = extractDomain(url)
  return domain?.replace(/^www\./, '') ?? null
}

export function extractTLD(hostname: string): string {
  const parts = hostname.split('.')
  return parts.slice(-2).join('.')
}

export function isValidDomain(domain: string): boolean {
  const pattern = /^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$/
  return pattern.test(domain)
}

export function normalizeDomain(domain: string): string {
  return domain.toLowerCase().replace(/^www\./, '')
}

export function isSameDomain(url1: string, url2: string): boolean {
  const d1 = extractHostname(url1)
  const d2 = extractHostname(url2)
  return d1 !== null && d2 !== null && d1 === d2
}

export function isInternalUrl(url: string): boolean {
  const internalPrefixes = ['chrome://', 'chrome-extension://', 'about:', 'moz-extension://', 'edge://']
  return internalPrefixes.some((prefix) => url.startsWith(prefix))
}

export function getTopLevelDomain(url: string): string | null {
  const hostname = extractHostname(url)
  if (!hostname) return null
  return extractTLD(hostname)
}

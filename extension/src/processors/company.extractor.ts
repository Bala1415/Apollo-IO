const PUBLIC_EMAIL_PROVIDERS = [
  'gmail.com',
  'yahoo.com',
  'hotmail.com',
  'outlook.com',
  'icloud.com',
  'aol.com',
  'protonmail.com',
  'zoho.com',
]

export interface CompanyIdentity {
  email: string | null
  domain: string | null
  name: string | null
  isBusinessEmail: boolean
}

export class CompanyExtractor {
  extractIdentity(email?: string | null): CompanyIdentity {
    if (!email) {
      return {
        email: null,
        domain: null,
        name: null,
        isBusinessEmail: false,
      }
    }

    const emailDomain = email.split('@')[1]?.toLowerCase()
    if (!emailDomain) {
      return {
        email,
        domain: null,
        name: null,
        isBusinessEmail: false,
      }
    }

    const isPublic = PUBLIC_EMAIL_PROVIDERS.includes(emailDomain)

    return {
      email,
      domain: isPublic ? null : emailDomain,
      name: isPublic ? null : this.extractCompanyName(emailDomain),
      isBusinessEmail: !isPublic,
    }
  }

  private extractCompanyName(domain: string): string {
    const root = domain.split('.')[0]
    if (!root) return domain
    // Capitalize first letter for best effort
    return root.charAt(0).toUpperCase() + root.slice(1)
  }
}

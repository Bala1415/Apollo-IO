import React, { useEffect, useState } from 'react'
import { useAuth } from '@/hooks'
import { usePermissions } from '@/hooks'
import { EXTENSION_VERSION } from '@/config'
import type { BrowserPayload, Interest } from '@ai-browser-intelligence/shared-types'
import type { BusinessIntentScores } from '@/processors/intent.engine'

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column' as const,
    minHeight: '480px',
    background: 'var(--color-surface-base)',
  },
  header: {
    padding: '20px 20px 16px',
    background: 'linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.08))',
    borderBottom: '1px solid var(--color-surface-border)',
  },
  logoRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '4px',
  },
  logoIcon: {
    width: 32,
    height: 32,
    borderRadius: '8px',
    background: 'linear-gradient(135deg, var(--color-brand-primary), var(--color-brand-secondary))',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '16px',
    boxShadow: 'var(--shadow-glow)',
  },
  title: {
    fontSize: '15px',
    fontWeight: 700,
    color: 'var(--color-text-primary)',
    letterSpacing: '-0.3px',
  },
  subtitle: {
    fontSize: '11px',
    color: 'var(--color-text-muted)',
    marginLeft: '42px',
  },
  body: {
    flex: 1,
    padding: '16px 20px',
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '12px',
    overflowY: 'auto' as const,
    maxHeight: '400px',
  },
  card: {
    background: 'var(--color-surface-elevated)',
    borderRadius: 'var(--radius-md)',
    padding: '14px 16px',
    border: '1px solid var(--color-surface-border)',
  },
  cardLabel: {
    fontSize: '11px',
    fontWeight: 600,
    color: 'var(--color-text-muted)',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.6px',
    marginBottom: '8px',
  },
  row: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  rowLabel: {
    fontSize: '13px',
    color: 'var(--color-text-secondary)',
  },
  badge: (variant: 'success' | 'warning' | 'error' | 'neutral') => {
    const colors = {
      success: { bg: 'rgba(16,185,129,0.15)', text: '#10b981' },
      warning: { bg: 'rgba(245,158,11,0.15)', text: '#f59e0b' },
      error: { bg: 'rgba(239,68,68,0.15)', text: '#ef4444' },
      neutral: { bg: 'rgba(100,116,139,0.15)', text: '#94a3b8' },
    }
    return {
      padding: '3px 10px',
      borderRadius: 'var(--radius-full)',
      fontSize: '11px',
      fontWeight: 600,
      background: colors[variant].bg,
      color: colors[variant].text,
    }
  },
  dot: (color: string) => ({
    width: 7,
    height: 7,
    borderRadius: '50%',
    background: color,
    display: 'inline-block',
    marginRight: '6px',
  }),
  loginBtn: {
    width: '100%',
    padding: '12px',
    borderRadius: 'var(--radius-md)',
    border: 'none',
    background: 'linear-gradient(135deg, var(--color-brand-primary), var(--color-brand-secondary))',
    color: 'white',
    fontSize: '14px',
    fontWeight: 600,
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    boxShadow: 'var(--shadow-glow)',
    transition: 'all var(--transition-fast)',
    fontFamily: 'var(--font-family-base)',
  },
  footer: {
    padding: '12px 20px',
    borderTop: '1px solid var(--color-surface-border)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  versionText: {
    fontSize: '11px',
    color: 'var(--color-text-muted)',
  },
  settingsLink: {
    fontSize: '11px',
    color: 'var(--color-brand-primary)',
    cursor: 'pointer',
    textDecoration: 'none',
    background: 'none',
    border: 'none',
    fontFamily: 'var(--font-family-base)',
  },
}

export const App: React.FC = () => {
  const { isAuthenticated, user, isLoading, signIn } = useAuth()
  const { allRequiredGranted, isLoading: permLoading } = usePermissions()

  const [payload, setPayload] = useState<BrowserPayload | null>(null)
  const [intent, setIntent] = useState<BusinessIntentScores | null>(null)
  const [interests, setInterests] = useState<Interest[]>([])

  useEffect(() => {
    chrome.storage.local.get(['latest_payload', 'latest_intent_scores', 'latest_interests'], (res) => {
      if (res.latest_payload) setPayload(res.latest_payload)
      if (res.latest_intent_scores) setIntent(res.latest_intent_scores)
      if (res.latest_interests) setInterests(res.latest_interests)
    })
  }, [])

  const openOptions = () => {
    void chrome.runtime.openOptionsPage()
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={styles.logoRow}>
          <div style={styles.logoIcon}>⚡</div>
          <span style={styles.title}>AI Browser Intelligence</span>
        </div>
        <span style={styles.subtitle}>Browser Intelligence Platform</span>
      </div>

      <div style={styles.body}>
        <div style={styles.card}>
          <div style={styles.cardLabel}>Identity</div>
          {isAuthenticated && user ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={styles.row}>
                <span style={styles.rowLabel}>{user.displayName}</span>
                <span style={styles.badge('success')}>
                  <span style={styles.dot('#10b981')} />
                  Active
                </span>
              </div>
              {payload?.user.companyDomain && (
                <div style={styles.row}>
                  <span style={{...styles.rowLabel, fontSize: '11px'}}>Company</span>
                  <span style={{ fontSize: '11px', fontWeight: 600 }}>{payload.user.companyDomain}</span>
                </div>
              )}
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={styles.row}>
                <span style={styles.rowLabel}>Not signed in</span>
                <span style={styles.badge('neutral')}>Offline</span>
              </div>
              <button
                id="popup-login-btn"
                style={styles.loginBtn}
                onClick={() => void signIn()}
                disabled={isLoading}
              >
                {isLoading ? '⟳ Signing in...' : '🔐 Sign in with Google'}
              </button>
            </div>
          )}
        </div>

        {payload && (
          <div style={styles.card}>
            <div style={styles.cardLabel}>Local Intelligence</div>
            <div style={styles.row}>
              <span style={styles.rowLabel}>Business Intent Score</span>
              <span style={styles.badge('neutral')}>{intent?.overallBusinessIntent || 0}/100</span>
            </div>
            <div style={{ ...styles.row, marginTop: '8px' }}>
              <span style={styles.rowLabel}>Top Categories</span>
              <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                {interests.slice(0, 2).map(i => i.categoryId.replace('cat_', '')).join(', ') || 'None'}
              </span>
            </div>
            <div style={{ ...styles.row, marginTop: '8px' }}>
              <span style={styles.rowLabel}>Business Domains Visited</span>
              <span style={{ fontSize: '11px', fontWeight: 600 }}>{payload.browsingSummary.businessDomains}</span>
            </div>
            <div style={{ ...styles.row, marginTop: '8px' }}>
              <span style={styles.rowLabel}>Last Generated</span>
              <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                {new Date(payload.timestamp).toLocaleTimeString()}
              </span>
            </div>
          </div>
        )}

        <div style={styles.card}>
          <div style={styles.cardLabel}>Permissions & Status</div>
          <div style={styles.row}>
            <span style={styles.rowLabel}>Permissions</span>
            {permLoading ? (
              <span style={styles.badge('neutral')}>Checking</span>
            ) : allRequiredGranted ? (
              <span style={styles.badge('success')}>
                <span style={styles.dot('#10b981')} />
                Granted
              </span>
            ) : (
              <span style={styles.badge('warning')}>
                <span style={styles.dot('#f59e0b')} />
                Missing
              </span>
            )}
          </div>
        </div>
      </div>

      <div style={styles.footer}>
        <span style={styles.versionText}>v{EXTENSION_VERSION}</span>
        <button id="popup-settings-btn" style={styles.settingsLink} onClick={openOptions}>
          Settings →
        </button>
      </div>
    </div>
  )
}

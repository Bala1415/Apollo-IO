import React, { useState } from 'react'
import { EXTENSION_VERSION } from '@/config'
import { useAuth, usePermissions } from '@/hooks'

type SettingsSection = 'authentication' | 'permissions' | 'privacy' | 'developer'

const NAV_ITEMS: { id: SettingsSection; label: string; icon: string }[] = [
  { id: 'authentication', label: 'Authentication', icon: '🔐' },
  { id: 'permissions', label: 'Permissions', icon: '🛡️' },
  { id: 'privacy', label: 'Privacy', icon: '🔒' },
  { id: 'developer', label: 'Developer', icon: '🛠️' },
]

const styles = {
  layout: { display: 'flex', minHeight: '100vh', width: '100%' },
  sidebar: {
    width: '220px',
    background: 'var(--color-surface-elevated)',
    borderRight: '1px solid var(--color-surface-border)',
    padding: '24px 0',
    flexShrink: 0,
  },
  sidebarHeader: {
    padding: '0 20px 20px',
    borderBottom: '1px solid var(--color-surface-border)',
    marginBottom: '8px',
  },
  sidebarTitle: {
    fontSize: '13px',
    fontWeight: 700,
    color: 'var(--color-text-primary)',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  navItem: (active: boolean) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '10px 20px',
    cursor: 'pointer',
    background: active ? 'rgba(99,102,241,0.12)' : 'transparent',
    borderRight: active ? '2px solid var(--color-brand-primary)' : '2px solid transparent',
    color: active ? 'var(--color-brand-primary)' : 'var(--color-text-secondary)',
    fontSize: '13px',
    fontWeight: active ? 600 : 400,
    transition: 'all 150ms ease',
    userSelect: 'none' as const,
  }),
  main: { flex: 1, padding: '40px', overflowY: 'auto' as const },
  pageHeader: { marginBottom: '32px' },
  pageTitle: {
    fontSize: '22px',
    fontWeight: 700,
    color: 'var(--color-text-primary)',
    marginBottom: '6px',
  },
  pageDesc: { fontSize: '14px', color: 'var(--color-text-secondary)' },
  section: {
    background: 'var(--color-surface-elevated)',
    border: '1px solid var(--color-surface-border)',
    borderRadius: 'var(--radius-lg)',
    padding: '24px',
    marginBottom: '16px',
  },
  sectionTitle: {
    fontSize: '14px',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
    marginBottom: '16px',
  },
  emptyState: {
    padding: '40px 0',
    textAlign: 'center' as const,
    color: 'var(--color-text-muted)',
    fontSize: '13px',
  },
  footer: {
    marginTop: '32px',
    paddingTop: '20px',
    borderTop: '1px solid var(--color-surface-border)',
    fontSize: '12px',
    color: 'var(--color-text-muted)',
  },
  button: {
    padding: '10px 16px',
    borderRadius: 'var(--radius-md)',
    border: 'none',
    background: 'var(--color-brand-primary)',
    color: 'white',
    fontSize: '13px',
    fontWeight: 600,
    cursor: 'pointer',
  }
}

const SECTION_CONFIG: Record<SettingsSection, { title: string; description: string }> = {
  authentication: {
    title: 'Authentication',
    description: 'Manage your Google account and authentication settings.',
  },
  permissions: {
    title: 'Permissions',
    description: 'Control which browser permissions the extension can access.',
  },
  privacy: {
    title: 'Privacy',
    description: 'Configure data collection, retention, and privacy preferences.',
  },
  developer: {
    title: 'Developer',
    description: 'Advanced settings for debugging and development.',
  },
}

export const App: React.FC = () => {
  const [activeSection, setActiveSection] = useState<SettingsSection>('authentication')
  const config = SECTION_CONFIG[activeSection]
  const { isAuthenticated, user, signIn, signOut, isLoading, error } = useAuth()
  const { allRequiredGranted, requestAll } = usePermissions()

  const handleResetStorage = async () => {
    if (confirm('Are you sure you want to clear all local extension data?')) {
      await chrome.storage.local.clear()
      alert('Local storage cleared. Please reload the extension.')
    }
  }

  const renderSectionContent = () => {
    switch (activeSection) {
      case 'authentication':
        return (
          <div style={styles.section}>
            <div style={styles.sectionTitle}>Google Account</div>
            {error && (
              <div style={{ padding: '12px', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', borderRadius: '6px', marginBottom: '16px', fontSize: '13px' }}>
                {error.message}
              </div>
            )}
            {isAuthenticated ? (
              <div>
                <p style={{ color: 'var(--color-text-secondary)', marginBottom: '16px' }}>Signed in as {user?.email}</p>
                <button style={styles.button} onClick={() => void signOut()} disabled={isLoading}>
                  {isLoading ? 'Signing out...' : 'Sign Out'}
                </button>
              </div>
            ) : (
              <div>
                <p style={{ color: 'var(--color-text-secondary)', marginBottom: '16px' }}>You are currently offline.</p>
                <button style={styles.button} onClick={() => void signIn()} disabled={isLoading}>
                  {isLoading ? 'Connecting...' : 'Sign in with Google'}
                </button>
              </div>
            )}
          </div>
        )
      case 'permissions':
        return (
          <div style={styles.section}>
            <div style={styles.sectionTitle}>Required Permissions</div>
            {allRequiredGranted ? (
              <p style={{ color: 'var(--color-text-secondary)' }}>All required permissions are granted.</p>
            ) : (
              <div>
                <p style={{ color: 'var(--color-text-secondary)', marginBottom: '16px' }}>Some permissions are missing.</p>
                <button style={styles.button} onClick={() => void requestAll()}>Grant Required Permissions</button>
              </div>
            )}
          </div>
        )
      case 'developer':
        return (
          <div style={styles.section}>
            <div style={styles.sectionTitle}>Local Storage Reset</div>
            <p style={{ color: 'var(--color-text-secondary)', marginBottom: '16px' }}>Clear all cached data and tokens.</p>
            <button style={{ ...styles.button, background: 'var(--color-danger-base)' }} onClick={() => void handleResetStorage()}>Clear Local Storage</button>
          </div>
        )
      default:
        return (
          <div style={styles.section}>
            <div style={styles.emptyState}>Configuration options coming in next phase</div>
          </div>
        )
    }
  }

  return (
    <div style={styles.layout}>
      <nav style={styles.sidebar}>
        <div style={styles.sidebarHeader}>
          <div style={styles.sidebarTitle}>
            <span>⚡</span>
            <span>AI Browser Intel</span>
          </div>
        </div>
        {NAV_ITEMS.map((item) => (
          <div
            key={item.id}
            style={styles.navItem(activeSection === item.id)}
            onClick={() => setActiveSection(item.id)}
            role="button"
            tabIndex={0}
            id={`nav-${item.id}`}
            onKeyDown={(e) => e.key === 'Enter' && setActiveSection(item.id)}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </div>
        ))}
      </nav>

      <main style={styles.main}>
        <div style={styles.pageHeader}>
          <h1 style={styles.pageTitle}>{config.title}</h1>
          <p style={styles.pageDesc}>{config.description}</p>
        </div>

        {renderSectionContent()}

        <div style={styles.footer}>
          AI Browser Intelligence Extension — v{EXTENSION_VERSION}
        </div>
      </main>
    </div>
  )
}

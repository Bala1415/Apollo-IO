export const ROUTES = {
  POPUP: {
    HOME: '/',
    LOGIN: '/login',
    PERMISSIONS: '/permissions',
    SETTINGS: '/settings',
  },
  OPTIONS: {
    AUTHENTICATION: '/authentication',
    PERMISSIONS: '/permissions',
    PRIVACY: '/privacy',
    DEVELOPER: '/developer',
  },
  API: {
    V1: '/api/v1',
  },
} as const

export const EXTERNAL_URLS = {
  PRIVACY_POLICY: 'https://yourdomain.com/privacy',
  TERMS_OF_SERVICE: 'https://yourdomain.com/terms',
  SUPPORT: 'https://yourdomain.com/support',
  DASHBOARD: 'https://dashboard.yourdomain.com',
} as const

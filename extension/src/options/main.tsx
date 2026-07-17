import React from 'react'
import { createRoot } from 'react-dom/client'
import { AuthProvider } from '@/auth'
import { App } from './App'
import './options.css'

const rootEl = document.getElementById('root')
if (!rootEl) throw new Error('Root element not found')

createRoot(rootEl).render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>
)

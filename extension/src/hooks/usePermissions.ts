import { useState, useEffect, useCallback } from 'react'
import type { PermissionState } from '@ai-browser-intelligence/shared-types'
import { PermissionManager } from '@/permissions'

interface UsePermissionsReturn {
  permissionState: PermissionState | null
  isLoading: boolean
  allRequiredGranted: boolean
  requestAll: () => Promise<void>
  refresh: () => Promise<void>
}

const manager = new PermissionManager()

export function usePermissions(): UsePermissionsReturn {
  const [permissionState, setPermissionState] = useState<PermissionState | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const refresh = useCallback(async () => {
    setIsLoading(true)
    try {
      const state = await manager.getPermissionState()
      setPermissionState(state)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const requestAll = useCallback(async () => {
    setIsLoading(true)
    try {
      const state = await manager.requestPermissions(['history', 'tabs', 'storage', 'identity', 'alarms'])
      setPermissionState(state)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  return {
    permissionState,
    isLoading,
    allRequiredGranted: permissionState?.allRequiredGranted ?? false,
    requestAll,
    refresh,
  }
}

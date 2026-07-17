import { useState, useCallback } from 'react'
import { LocalStorageService } from '@/storage'

const storage = new LocalStorageService()

interface UseStorageReturn<T> {
  value: T | null
  loading: boolean
  set: (value: T) => Promise<void>
  remove: () => Promise<void>
}

export function useStorage<T>(key: string, initialValue?: T): UseStorageReturn<T> {
  const [value, setValue] = useState<T | null>(initialValue ?? null)
  const [loading, setLoading] = useState(false)

  const set = useCallback(
    async (newValue: T) => {
      setLoading(true)
      try {
        await storage.set(key, newValue)
        setValue(newValue)
      } finally {
        setLoading(false)
      }
    },
    [key]
  )

  const remove = useCallback(async () => {
    setLoading(true)
    try {
      await storage.remove(key)
      setValue(null)
    } finally {
      setLoading(false)
    }
  }, [key])

  return { value, loading, set, remove }
}

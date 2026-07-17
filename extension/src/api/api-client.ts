import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios'
import type { ApiResponse } from '@ai-browser-intelligence/shared-types'
import { loadConfiguration } from '@/config'
import { TIMING } from '@/config'
import { createLogger } from '@/logger'

const logger = createLogger('ApiClient')

let axiosInstance: AxiosInstance | null = null

async function createAxiosInstance(): Promise<AxiosInstance> {
  const config = await loadConfiguration()

  const instance = axios.create({
    baseURL: `${config.apiBaseUrl}/api/${config.apiVersion}`,
    timeout: TIMING.REQUEST_TIMEOUT_MS,
    headers: {
      'Content-Type': 'application/json',
      'X-Extension-Version': config.version,
      'X-Client': 'ai-browser-intelligence-extension',
    },
  })

  instance.interceptors.request.use(
    async (reqConfig: InternalAxiosRequestConfig) => {
      const tokenKey = 'auth_token'
      const stored = await chrome.storage.local.get(tokenKey)
      const token = stored[tokenKey] as string | undefined
      if (token) {
        reqConfig.headers.set('Authorization', `Bearer ${token}`)
      }
      return reqConfig
    },
    (error: unknown) => {
      logger.error('Request interceptor error', error)
      return Promise.reject(error)
    }
  )

  instance.interceptors.response.use(
    (response) => response,
    async (error: unknown) => {
      logger.error('API request failed', error)
      return Promise.reject(error)
    }
  )

  return instance
}

export async function getApiClient(): Promise<AxiosInstance> {
  if (!axiosInstance) {
    axiosInstance = await createAxiosInstance()
  }
  return axiosInstance
}

export async function apiGet<T>(
  path: string,
  config?: AxiosRequestConfig
): Promise<ApiResponse<T>> {
  const client = await getApiClient()
  const response = await client.get<ApiResponse<T>>(path, config)
  return response.data
}

export async function apiPost<T>(
  path: string,
  body: unknown,
  config?: AxiosRequestConfig
): Promise<ApiResponse<T>> {
  const client = await getApiClient()
  const response = await client.post<ApiResponse<T>>(path, body, config)
  return response.data
}

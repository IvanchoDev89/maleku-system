export const useApi = () => {
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBase as string || 'http://localhost:8000/api/v1'

  // SECURITY: enforce HTTPS in production builds. Sending JWT tokens over
  // plain HTTP would allow network attackers to steal sessions.
  if (import.meta.env.PROD && baseURL.startsWith('http://')) {
    throw new Error('API base must use HTTPS in production (got ' + baseURL + ')')
  }

  const tryRefreshToken = async (): Promise<boolean> => {
    try {
      const auth = useAuthStore()
      return await auth.refreshToken()
    } catch {
      return false
    }
  }

  const fetchApi = async <T>(
    endpoint: string,
    options: {
      method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
      body?: any
      params?: Record<string, any>
      headers?: Record<string, string>
      retryCount?: number
    } = {}
  ): Promise<T> => {
    const auth = useAuthStore()
    const token = auth.token

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    let url = `${baseURL}${endpoint}`

    if (options.params) {
      const params = new URLSearchParams(options.params)
      url += `?${params}`
    }

    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 30000)

    try {
      const response = await $fetch<T>(url, {
        method: options.method || 'GET',
        body: options.body,
        headers,
        signal: controller.signal
      })
      return response
    } catch (error: any) {
      if (error.name === 'AbortError') {
        throw { status: 408, data: { detail: 'Request timed out' } }
      }

      if (error.response?.status === 401 && endpoint !== '/auth/refresh') {
        const refreshed = await tryRefreshToken()
        if (refreshed) {
          const retryCount = options.retryCount ?? 0
          if (retryCount < 1) {
            const newToken = useAuthStore().token
            headers['Authorization'] = `Bearer ${newToken}`
            return fetchApi<T>(endpoint, { ...options, retryCount: retryCount + 1 })
          }
        }
      }

      console.error(`API Error [${options.method || 'GET'} ${endpoint}]:`, error)
      useToast().add(`API Error: ${error?.status || ''} ${endpoint}`.trim(), 'error')

      if (error.response) {
        throw {
          status: error.response.status,
          data: error.response._data || error.response.data
        }
      }
      throw error
    } finally {
      clearTimeout(timeout)
    }
  }

  const upload = async <T>(
    endpoint: string,
    body: FormData
  ): Promise<T> => {
    const auth = useAuthStore()
    const token = auth.token

    const headers: Record<string, string> = {}
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 30000)

    try {
      const response = await $fetch<T>(`${baseURL}${endpoint}`, {
        method: 'POST',
        body,
        headers,
        signal: controller.signal
      })
      return response
    } catch (error: any) {
      if (error.name === 'AbortError') {
        throw { status: 408, data: { detail: 'Upload timed out' } }
      }
      console.error(`Upload Error [${endpoint}]:`, error)
      useToast().add(`Upload failed: ${endpoint}`, 'error')
      if (error.response) {
        throw {
          status: error.response.status,
          data: error.response._data || error.response.data
        }
      }
      throw error
    } finally {
      clearTimeout(timeout)
    }
  }

  const uploadFile = async <T>(
    endpoint: string,
    file: File | Blob,
    filename: string = 'file',
    folder: string = 'general'
  ): Promise<T> => {
    const formData = new FormData()
    formData.append(filename, file)
    formData.append('folder', folder)
    return upload<T>(endpoint, formData)
  }

  const uploadFiles = async <T>(
    endpoint: string,
    files: FileList | File[],
    folder: string = 'gallery'
  ): Promise<T> => {
    const formData = new FormData()
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i])
    }
    formData.append('folder', folder)
    return upload<T>(endpoint, formData)
  }

  return {
    get: <T>(endpoint: string, params?: Record<string, any>) =>
      fetchApi<T>(endpoint, { method: 'GET', params }),

    post: <T>(endpoint: string, body?: any) =>
      fetchApi<T>(endpoint, { method: 'POST', body }),

    put: <T>(endpoint: string, body?: any) =>
      fetchApi<T>(endpoint, { method: 'PUT', body }),

    patch: <T>(endpoint: string, body?: any) =>
      fetchApi<T>(endpoint, { method: 'PATCH', body }),

    delete: <T>(endpoint: string) =>
      fetchApi<T>(endpoint, { method: 'DELETE' }),

    upload: uploadFile,
    uploadMultiple: uploadFiles
  }
}

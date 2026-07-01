import { defineStore } from 'pinia'
import type { User } from '~/types'

// === HELPERS para SessionStorage (elimina duplicación) ===
const STORAGE_KEYS = {
  token: 'token',
  refreshToken: 'refreshToken',
  user: 'user'
} as const

function persistAuthToSession(
  token: string,
  refreshToken: string,
  user: User
): void {
  if (!process.client) return
  sessionStorage.setItem(STORAGE_KEYS.token, token)
  sessionStorage.setItem(STORAGE_KEYS.refreshToken, refreshToken)
  sessionStorage.setItem(STORAGE_KEYS.user, JSON.stringify(user))
}

function clearAuthFromSession(): void {
  if (!process.client) return
  sessionStorage.removeItem(STORAGE_KEYS.token)
  sessionStorage.removeItem(STORAGE_KEYS.refreshToken)
  sessionStorage.removeItem(STORAGE_KEYS.user)
}

function loadAuthFromSession(): { token: string | null; refreshToken: string | null; user: User | null } {
  if (!process.client) return { token: null, refreshToken: null, user: null }

  const token = sessionStorage.getItem(STORAGE_KEYS.token)
  const refreshToken = sessionStorage.getItem(STORAGE_KEYS.refreshToken)
  const userStr = sessionStorage.getItem(STORAGE_KEYS.user)

  let user: User | null = null
  if (userStr) {
    try {
      user = JSON.parse(userStr)
    } catch {
      clearAuthFromSession()
    }
  }

  return { token, refreshToken, user }
}

interface AuthState {
  user: User | null
  token: string | null
  // NOTE: state slot is named `refreshTokenValue` to avoid shadowing the
  // `refreshToken` action below (Pinia would otherwise resolve the action
  // when `this.refreshToken` is read, masking the stored token).
  refreshTokenValue: string | null
  isAuthenticated: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: null,
    refreshTokenValue: null,
    isAuthenticated: false
  }),

  getters: {
    isVendor: (state) => state.user?.role === 'vendor',
    isAdmin: (state) => ['super_admin', 'admin'].includes(state.user?.role || ''),
    isSuperAdmin: (state) => state.user?.role === 'super_admin',
    isClient: (state) => state.user?.role === 'client',
    isAgent: (state) => state.user?.role === 'agent',
    isCustomerService: (state) => state.user?.role === 'customer_service'
  },

  actions: {
    async login(email: string, password: string): Promise<{ success: boolean; error?: string; user?: User }> {
      let api: ReturnType<typeof useApi>
      try {
        api = useApi()
      } catch (e: any) {
        return { success: false, error: 'Error al inicializar conexión API' }
      }

      try {
        const response = await api.post<{
          access_token: string
          refresh_token: string
          user: User
        }>('/auth/login', { email, password })

        this.token = response.access_token
        this.refreshTokenValue = response.refresh_token
        this.user = response.user
        this.isAuthenticated = true

        persistAuthToSession(response.access_token, response.refresh_token, response.user)

        return { success: true, user: response.user }
      } catch (error: any) {
        return {
          success: false,
          error: error?.data?.detail || error?.message || 'Error al iniciar sesión'
        }
      }
    },

    async register(userData: {
      email: string
      password: string
      full_name: string
      phone?: string
    }): Promise<{ success: boolean; error?: string }> {
      const api = useApi()

      try {
        const response = await api.post<{
          access_token: string
          refresh_token: string
          user: User
        }>('/auth/register', userData)

        this.token = response.access_token
        this.refreshTokenValue = response.refresh_token
        this.user = response.user
        this.isAuthenticated = true

        persistAuthToSession(response.access_token, response.refresh_token, response.user)

        return { success: true }
      } catch (error: any) {
        return {
          success: false,
          error: error?.data?.detail || error?.message || 'Error al registrar'
        }
      }
    },

    async registerVendor(userData: {
      email: string
      password: string
      full_name: string
      phone?: string
      business_name: string
      business_type: string
    }): Promise<{ success: boolean; error?: string }> {
      const api = useApi()

      try {
        const response = await api.post<{
          access_token: string
          refresh_token: string
          user: User
        }>('/auth/register/vendor', {
          email: userData.email,
          password: userData.password,
          full_name: userData.full_name,
          phone: userData.phone,
          business_name: userData.business_name,
          business_type: userData.business_type
        })

        this.token = response.access_token
        this.refreshTokenValue = response.refresh_token
        this.user = response.user
        this.isAuthenticated = true

        persistAuthToSession(response.access_token, response.refresh_token, response.user)

        return { success: true }
      } catch (error: any) {
        return {
          success: false,
          error: error?.data?.detail || error?.message || 'Error al registrar vendor'
        }
      }
    },

    async logout() {
      this.user = null
      this.token = null
      this.refreshTokenValue = null
      this.isAuthenticated = false

      clearAuthFromSession()
      if (process.client) {
        localStorage.removeItem('remembered_session')
      }
    },

    async refreshToken() {
      if (!this.refreshTokenValue) return false

      const api = useApi()

      try {
        const response = await api.post<{
          access_token: string
          refresh_token: string
          user: User
        }>('/auth/refresh', { refresh_token: this.refreshTokenValue })

        this.token = response.access_token
        this.refreshTokenValue = response.refresh_token
        this.user = response.user

        persistAuthToSession(response.access_token, response.refresh_token, response.user)

        return true
      } catch {
        await this.logout()
        return false
      }
    },

    initAuth() {
      const { token, refreshToken, user } = loadAuthFromSession()

      if (token && user) {
        this.token = token
        this.refreshTokenValue = refreshToken
        this.user = user
        this.isAuthenticated = true
      }
    }
  }
})

// NOTA: useAuth() eliminado - era redundante. useAuthStore() ya expone todo directamente.
// Uso: const auth = useAuthStore() // tiene token, user, isAuthenticated, getters, actions

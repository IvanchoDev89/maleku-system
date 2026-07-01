import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import type { User } from '~/types'

let mockUseApiFn: () => any
const mockPost = vi.fn()

vi.mock('~/composables/useApi', () => ({
  useApi: () => mockUseApiFn(),
}))

const mockApi = {
  get: vi.fn(),
  post: mockPost,
  put: vi.fn(),
  patch: vi.fn(),
  delete: vi.fn(),
  upload: vi.fn(),
  uploadMultiple: vi.fn(),
}

const createMockUser = (overrides: Partial<User> = {}): User => ({
  id: 'user-1',
  email: 'test@example.com',
  full_name: 'Test User',
  phone: '+50688888888',
  role: 'client',
  is_verified: true,
  created_at: new Date().toISOString(),
  ...overrides,
})

import { useAuthStore } from '~/stores/auth'

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    sessionStorage.clear()
    mockUseApiFn = () => mockApi
  })

  describe('login', () => {
    it('should login successfully and persist to sessionStorage', async () => {
      const user = createMockUser()
      mockPost.mockResolvedValue({
        access_token: 'token-123',
        refresh_token: 'refresh-456',
        user,
      })

      const auth = useAuthStore()
      const result = await auth.login('test@example.com', 'password')

      expect(result.success).toBe(true)
      expect(result.user).toEqual(user)
      expect(auth.token).toBe('token-123')
      expect(auth.refreshTokenValue).toBe('refresh-456')
      expect(auth.user).toEqual(user)
      expect(auth.isAuthenticated).toBe(true)

      expect(sessionStorage.getItem('token')).toBe('token-123')
      expect(sessionStorage.getItem('refreshToken')).toBe('refresh-456')
      expect(sessionStorage.getItem('user')).toBe(JSON.stringify(user))
    })

    it('should return error on API failure', async () => {
      mockPost.mockRejectedValue({ data: { detail: 'Invalid credentials' } })

      const auth = useAuthStore()
      const result = await auth.login('bad@email.com', 'wrong')

      expect(result.success).toBe(false)
      expect(result.error).toBe('Invalid credentials')
      expect(auth.isAuthenticated).toBe(false)
    })

    it('should handle useApi() initialization error', async () => {
      mockUseApiFn = () => { throw new Error('init failed') }

      const auth = useAuthStore()
      const result = await auth.login('test@example.com', 'password')

      expect(result.success).toBe(false)
      expect(result.error).toBe('Error al inicializar conexión API')
    })

    it('should handle error without data.detail', async () => {
      mockPost.mockRejectedValue({ message: 'Generic error' })

      const auth = useAuthStore()
      const result = await auth.login('test@example.com', 'password')
      expect(result.error).toBe('Generic error')
    })

    it('should handle error with neither data nor message', async () => {
      mockPost.mockRejectedValue({})

      const auth = useAuthStore()
      const result = await auth.login('test@example.com', 'password')
      expect(result.error).toBe('Error al iniciar sesión')
    })
  })

  describe('register', () => {
    it('should register successfully and persist to sessionStorage', async () => {
      const user = createMockUser()
      mockPost.mockResolvedValue({
        access_token: 'token-reg',
        refresh_token: 'refresh-reg',
        user,
      })

      const auth = useAuthStore()
      const result = await auth.register({
        email: 'new@example.com',
        password: 'Secure123!',
        full_name: 'New User',
      })

      expect(result.success).toBe(true)
      expect(auth.token).toBe('token-reg')
      expect(auth.isAuthenticated).toBe(true)
    })

    it('should return error on duplicate email', async () => {
      mockPost.mockRejectedValue({ data: { detail: 'Email already registered' } })

      const auth = useAuthStore()
      const result = await auth.register({
        email: 'dup@example.com',
        password: 'Secure123!',
        full_name: 'Dup',
      })

      expect(result.success).toBe(false)
      expect(result.error).toBe('Email already registered')
    })
  })

  describe('registerVendor', () => {
    it('should register vendor successfully', async () => {
      const user = createMockUser({ role: 'vendor' })
      mockPost.mockResolvedValue({
        access_token: 'token-vendor',
        refresh_token: 'refresh-vendor',
        user,
      })

      const auth = useAuthStore()
      const result = await auth.registerVendor({
        email: 'vendor@example.com',
        password: 'Secure123!',
        full_name: 'Vendor User',
        business_name: 'Test Tours CR',
        business_type: 'tour_operator',
      })

      expect(result.success).toBe(true)
      expect(auth.user?.role).toBe('vendor')
    })

    it('should return error on vendor registration failure', async () => {
      mockPost.mockRejectedValue({ data: { detail: 'Business name already taken' } })

      const auth = useAuthStore()
      const result = await auth.registerVendor({
        email: 'vendor@example.com',
        password: 'Secure123!',
        full_name: 'Vendor User',
        business_name: 'Existing Tours',
        business_type: 'tour_operator',
      })

      expect(result.success).toBe(false)
    })
  })

  describe('logout', () => {
    it('should clear state and sessionStorage', async () => {
      sessionStorage.setItem('token', 'some-token')
      sessionStorage.setItem('refreshToken', 'some-refresh')
      sessionStorage.setItem('user', JSON.stringify(createMockUser()))

      const auth = useAuthStore()
      auth.token = 'some-token'
      auth.refreshTokenValue = 'some-refresh'
      auth.user = createMockUser()
      auth.isAuthenticated = true

      await auth.logout()

      expect(auth.token).toBeNull()
      expect(auth.refreshTokenValue).toBeNull()
      expect(auth.user).toBeNull()
      expect(auth.isAuthenticated).toBe(false)
      expect(sessionStorage.getItem('token')).toBeNull()
      expect(sessionStorage.getItem('refreshToken')).toBeNull()
      expect(sessionStorage.getItem('user')).toBeNull()
    })
  })

  describe('refreshToken', () => {
    it('should refresh token successfully', async () => {
      const user = createMockUser()
      mockPost.mockResolvedValue({
        access_token: 'new-token',
        refresh_token: 'new-refresh',
        user,
      })

      const auth = useAuthStore()
      auth.refreshTokenValue = 'old-refresh'

      const result = await auth.refreshToken()
      expect(result).toBe(true)
      expect(auth.token).toBe('new-token')
      expect(auth.refreshTokenValue).toBe('new-refresh')
    })

    it('should return false if no refresh token available', async () => {
      const auth = useAuthStore()

      const result = await auth.refreshToken()
      expect(result).toBe(false)
    })

    it('should logout on refresh failure', async () => {
      mockPost.mockRejectedValue(new Error('Token expired'))

      const auth = useAuthStore()
      auth.token = 'old-token'
      auth.refreshTokenValue = 'expired-refresh'
      auth.user = createMockUser()
      auth.isAuthenticated = true

      const result = await auth.refreshToken()
      expect(result).toBe(false)
      expect(auth.token).toBeNull()
      expect(auth.isAuthenticated).toBe(false)
    })
  })

  describe('initAuth', () => {
    it('should restore session from sessionStorage', async () => {
      const user = createMockUser()
      sessionStorage.setItem('token', 'stored-token')
      sessionStorage.setItem('refreshToken', 'stored-refresh')
      sessionStorage.setItem('user', JSON.stringify(user))

      const auth = useAuthStore()
      auth.initAuth()

      expect(auth.token).toBe('stored-token')
      expect(auth.refreshTokenValue).toBe('stored-refresh')
      expect(auth.user).toEqual(user)
      expect(auth.isAuthenticated).toBe(true)
    })

    it('should do nothing if no token in sessionStorage', async () => {
      const auth = useAuthStore()

      auth.initAuth()
      expect(auth.token).toBeNull()
      expect(auth.isAuthenticated).toBe(false)
    })

    it('should clear session on corrupted user data', async () => {
      sessionStorage.setItem('token', 'stored-token')
      sessionStorage.setItem('refreshToken', 'stored-refresh')
      sessionStorage.setItem('user', '{corrupted-json')

      const auth = useAuthStore()
      auth.initAuth()

      expect(auth.token).toBeNull()
      expect(sessionStorage.getItem('token')).toBeNull()
    })
  })

  describe('getters', () => {
    it('should identify vendor role', async () => {
      const auth = useAuthStore()
      auth.user = createMockUser({ role: 'vendor' })

      expect(auth.isVendor).toBe(true)
      expect(auth.isAdmin).toBe(false)
      expect(auth.isClient).toBe(false)
      expect(auth.isSuperAdmin).toBe(false)
    })

    it('should identify super_admin role', async () => {
      const auth = useAuthStore()
      auth.user = createMockUser({ role: 'super_admin' })

      expect(auth.isSuperAdmin).toBe(true)
      expect(auth.isAdmin).toBe(true)
      expect(auth.isVendor).toBe(false)
      expect(auth.isClient).toBe(false)
    })

    it('should identify client role', async () => {
      const auth = useAuthStore()
      auth.user = createMockUser({ role: 'client' })

      expect(auth.isClient).toBe(true)
      expect(auth.isAdmin).toBe(false)
      expect(auth.isSuperAdmin).toBe(false)
    })

    it('should handle null user in getters', async () => {
      const auth = useAuthStore()
      auth.user = null

      expect(auth.isVendor).toBe(false)
      expect(auth.isAdmin).toBe(false)
      expect(auth.isClient).toBe(false)
      expect(auth.isSuperAdmin).toBe(false)
    })
  })
})

import { vi } from 'vitest'
import type { Ref, ComputedRef } from 'vue'

type MockNuxtOptions = {
  apiBase?: string
  isAuthenticated?: boolean
  token?: string | null
  userRole?: string | null
  navigateTo?: typeof navigateTo
}

export function createMockNuxtEnv(opts: MockNuxtOptions = {}) {
  const apiBase = opts.apiBase ?? '/api/v1'

  const mockRuntimeConfig = {
    public: {
      apiBase,
      siteUrl: 'https://costaricatravel.dev',
      cdnUrl: '',
      siteName: 'Costa Rica Travel',
      siteDescription: 'Test description',
      siteTitleTemplate: '%s - Costa Rica Travel',
      sentryDsn: '',
      stripeKey: '',
      siteKeywords: 'test, keywords',
      environment: 'test',
    },
  }

  const mockAuthState = {
    token: opts.token ?? null,
    refreshTokenValue: null,
    user: opts.userRole ? { id: 'mock-id', role: opts.userRole, email: 'test@test.com', full_name: 'Test', phone: null, is_verified: true, created_at: new Date().toISOString() } : null,
    isAuthenticated: opts.isAuthenticated ?? false,
    isVendor: opts.userRole === 'vendor',
    isAdmin: opts.userRole === 'super_admin' || opts.userRole === 'admin',
    isSuperAdmin: opts.userRole === 'super_admin',
    isClient: opts.userRole === 'client',
    isAgent: opts.userRole === 'agent',
    isCustomerService: opts.userRole === 'customer_service',
    login: vi.fn(),
    register: vi.fn(),
    registerVendor: vi.fn(),
    logout: vi.fn(),
    refreshToken: vi.fn().mockResolvedValue(false),
    initAuth: vi.fn(),
  }

  const mockApi = {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
    upload: vi.fn(),
    uploadMultiple: vi.fn(),
  }

  return {
    mockRuntimeConfig,
    mockAuthState,
    mockApi,
    install() {
      vi.stubGlobal('useRuntimeConfig', vi.fn(() => mockRuntimeConfig))
      vi.stubGlobal('useAuthStore', vi.fn(() => mockAuthState))
      vi.stubGlobal('useApi', vi.fn(() => mockApi))
      vi.stubGlobal('navigateTo', vi.fn())
      vi.stubGlobal('useHead', vi.fn())
      vi.stubGlobal('useLocalePath', vi.fn(() => (path: string) => path))
      vi.stubGlobal('useRouter', vi.fn(() => ({
        push: vi.fn(),
        replace: vi.fn(),
        currentRoute: { value: { path: '/', query: {} } },
      })))
      vi.stubGlobal('useRoute', vi.fn(() => ({
        path: '/',
        query: {},
        params: {},
        fullPath: '/',
      })))
    },
  }
}

import { describe, it, expect, vi, beforeEach } from 'vitest'

const mockGet = vi.fn()
let mockIsAuthenticated = false

vi.mock('~/composables/useApi', () => ({
  useApi: () => ({
    get: mockGet,
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
    upload: vi.fn(),
    uploadMultiple: vi.fn(),
  }),
}))

vi.mock('~/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    get isAuthenticated() { return mockIsAuthenticated },
    token: null,
    user: null,
    refreshToken: vi.fn(),
    logout: vi.fn(),
  })),
}))

import { useNotifications } from '~/composables/useNotifications'

describe('useNotifications', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    mockIsAuthenticated = true
  })

  it('should return count=0 and loading=false initially', () => {
    const { count, loading } = useNotifications()
    expect(count.value).toBe(0)
    expect(loading.value).toBe(false)
  })

  it('should fetch count and update reactive refs', async () => {
    mockGet.mockResolvedValue([{ id: 1 }, { id: 2 }])

    const notifications = useNotifications()
    const fetchPromise = notifications.fetchCount()
    expect(notifications.loading.value).toBe(true)
    await fetchPromise
    expect(notifications.count.value).toBe(2)
    expect(notifications.loading.value).toBe(false)
  })

  it('should not fetch if not authenticated', async () => {
    mockIsAuthenticated = false
    const notifications = useNotifications()
    await notifications.fetchCount()
    expect(mockGet).not.toHaveBeenCalled()
    expect(notifications.count.value).toBe(0)
  })

  it('should set count=0 on fetch error', async () => {
    mockGet.mockRejectedValue(new Error('network error'))
    const notifications = useNotifications()
    await notifications.fetchCount()
    expect(notifications.count.value).toBe(0)
  })

  it('should start polling at given interval', async () => {
    mockGet.mockResolvedValue([{ id: 1 }])

    const notifications = useNotifications()
    mockGet.mockClear()

    notifications.startPolling(1000)

    expect(mockGet).toHaveBeenCalledTimes(1)

    vi.advanceTimersByTime(1000)
    expect(mockGet).toHaveBeenCalledTimes(2)

    notifications.stopPolling()
    vi.advanceTimersByTime(5000)
    expect(mockGet).toHaveBeenCalledTimes(2)
  })

  it('should not start polling if not authenticated', () => {
    mockIsAuthenticated = false
    const notifications = useNotifications()
    expect(mockGet).not.toHaveBeenCalled()
  })
})

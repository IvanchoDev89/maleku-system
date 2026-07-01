import { vi, beforeEach } from 'vitest'

beforeEach(() => {
  vi.unstubAllGlobals()
  vi.unstubAllEnvs()
  sessionStorage.clear()
})

import { vi } from 'vitest'

export function setup() {
  process.env.NUXT_PUBLIC_API_URL = '/api/v1'
}

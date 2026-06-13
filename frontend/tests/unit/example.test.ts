import { describe, it, expect } from 'vitest'

describe('example test suite', () => {
  it('should pass sanity check', () => {
    expect(1 + 1).toBe(2)
  })

  it('should have correct environment', () => {
    expect(typeof window).toBe('object')
  })
})

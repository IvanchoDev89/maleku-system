import { describe, it, expect } from 'vitest'

// Pure JS formatting functions extracted from composables/useDashboard
function formatNumber(num: number): string {
  if (!num) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

function formatTimeAgo(timestamp: string): string {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000)
  if (diff < 60) return 'hace un momento'
  if (diff < 3600) return `hace ${Math.floor(diff / 60)} minutos`
  if (diff < 86400) return `hace ${Math.floor(diff / 3600)} horas`
  return `hace ${Math.floor(diff / 86400)} días`
}

describe('formatNumber', () => {
  it('returns "0" for null/undefined/0', () => {
    expect(formatNumber(null as any)).toBe('0')
    expect(formatNumber(undefined as any)).toBe('0')
    expect(formatNumber(0)).toBe('0')
  })

  it('returns number as string for values < 1000', () => {
    expect(formatNumber(42)).toBe('42')
    expect(formatNumber(999)).toBe('999')
  })

  it('formats thousands with K suffix', () => {
    expect(formatNumber(1000)).toBe('1.0K')
    expect(formatNumber(1500)).toBe('1.5K')
  })

  it('formats millions with M suffix', () => {
    expect(formatNumber(1000000)).toBe('1.0M')
    expect(formatNumber(2500000)).toBe('2.5M')
  })
})

describe('formatTimeAgo', () => {
  it('returns "hace un momento" for recent timestamps (<60s)', () => {
    const now = new Date().toISOString()
    expect(formatTimeAgo(now)).toBe('hace un momento')
  })

  it('returns minutes ago', () => {
    const past = new Date(Date.now() - 120 * 1000).toISOString()
    expect(formatTimeAgo(past)).toBe('hace 2 minutos')
  })

  it('returns hours ago', () => {
    const past = new Date(Date.now() - 7200 * 1000).toISOString()
    expect(formatTimeAgo(past)).toBe('hace 2 horas')
  })

  it('returns days ago', () => {
    const past = new Date(Date.now() - 3 * 86400 * 1000).toISOString()
    expect(formatTimeAgo(past)).toBe('hace 3 días')
  })
})

describe('formatNumber edge cases', () => {
  it('handles negative numbers', () => {
    expect(formatNumber(-5)).toBe('-5')
  })

  it('handles decimal numbers', () => {
    expect(formatNumber(3.14)).toBe('3.14')
  })

  it('handles exactly 1000', () => {
    expect(formatNumber(1000)).toBe('1.0K')
  })

  it('handles exactly 1000000', () => {
    expect(formatNumber(1000000)).toBe('1.0M')
  })

  it('handles large numbers with decimal', () => {
    expect(formatNumber(1234567)).toBe('1.2M')
  })
})

import { describe, it, expect, vi } from 'vitest'
import { useAsyncAction } from '~/composables/useAsyncAction'

describe('useAsyncAction', () => {
  it('should start with pending=false and error=null', () => {
    const { pending, error } = useAsyncAction({ defaultValue: null })
    expect(pending.value).toBe(false)
    expect(error.value).toBeNull()
  })

  it('should set pending=true during execution', async () => {
    const { pending, execute } = useAsyncAction({ defaultValue: null })
    const promise = execute(() => new Promise<string>(resolve => setTimeout(resolve, 50)))
    expect(pending.value).toBe(true)
    await promise
    expect(pending.value).toBe(false)
  })

  it('should return the resolved value', async () => {
    const { execute } = useAsyncAction({ defaultValue: null })
    const result = await execute(async () => 'hello')
    expect(result).toBe('hello')
  })

  it('should set error on rejection and return default value', async () => {
    const { error, execute } = useAsyncAction({ defaultValue: 0 })
    const result = await execute(async () => { throw new Error('oops') })
    expect(error.value).toBe('oops')
    expect(result).toBe(0)
  })

  it('should extract detail from API error objects', async () => {
    const { error, execute } = useAsyncAction({ defaultValue: null })
    await execute(async () => { throw { data: { detail: 'Bad request' }, status: 400 } })
    expect(error.value).toBe('Bad request')
  })

  it('should not set error when silent=true', async () => {
    const { error, execute } = useAsyncAction({ defaultValue: 0 })
    await execute(async () => { throw new Error('silent fail') }, { silent: true })
    expect(error.value).toBeNull()
  })

  it('should support custom defaultValue per call', async () => {
    const { execute } = useAsyncAction({ defaultValue: 0 })
    const result = await execute(async () => { throw new Error('fail') }, { defaultValue: -1 })
    expect(result).toBe(-1)
  })

  it('should clear error on new execution', async () => {
    const { error, execute } = useAsyncAction({ defaultValue: 0 })
    await execute(async () => { throw new Error('first') })
    expect(error.value).toBe('first')
    await execute(async () => 42)
    expect(error.value).toBeNull()
  })
})

import { ref } from 'vue'

interface AsyncActionOptions<T> {
  defaultValue: T
}

export function useAsyncAction<T>(options: AsyncActionOptions<T>) {
  const pending = ref(false)
  const error = ref<string | null>(null)

  async function execute(fn: () => Promise<T>, opts?: { defaultValue?: T; silent?: boolean }): Promise<T> {
    pending.value = true
    error.value = null
    try {
      return await fn()
    } catch (e: any) {
      const message = e?.data?.detail || e?.message || 'An error occurred'
      if (!opts?.silent) {
        error.value = message
      }
      return (opts?.defaultValue ?? options.defaultValue) as T
    } finally {
      pending.value = false
    }
  }

  return { pending, error, execute }
}

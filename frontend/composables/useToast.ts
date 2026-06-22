import { ref } from 'vue'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface Toast {
  id: string
  message: string
  type: ToastType
  duration?: number
}

const toasts = ref<Toast[]>([])

let nextId = 0

const MAX_TOASTS = 50

export function useToast() {
  function add(message: string, type: ToastType = 'info', duration = 4000) {
    const id = `toast-${++nextId}`
    toasts.value.push({ id, message, type, duration })
    if (toasts.value.length > MAX_TOASTS) {
      toasts.value.splice(0, toasts.value.length - MAX_TOASTS)
    }
    if (duration > 0) {
      setTimeout(() => remove(id), duration)
    }
    return id
  }

  function remove(id: string) {
    const idx = toasts.value.findIndex(t => t.id === id)
    if (idx !== -1) toasts.value.splice(idx, 1)
  }

  function success(message: string) { return add(message, 'success') }
  function error(message: string) { return add(message, 'error', 6000) }
  function warning(message: string) { return add(message, 'warning', 5000) }
  function info(message: string) { return add(message, 'info') }

  return { toasts, add, remove, success, error, warning, info }
}

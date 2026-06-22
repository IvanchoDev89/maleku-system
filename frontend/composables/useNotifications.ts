export function useNotifications() {
  const api = useApi()
  const count = ref(0)
  const loading = ref(false)

  const fetchCount = async () => {
    loading.value = true
    try {
      const alerts = await api.get<any[]>('/superadmin/dashboard/alerts')
      count.value = alerts?.length || 0
    } catch {
      count.value = 0
    } finally {
      loading.value = false
    }
  }

  let pollTimer: ReturnType<typeof setInterval> | null = null

  const startPolling = (interval = 60000) => {
    fetchCount()
    pollTimer = setInterval(fetchCount, interval)
  }

  const stopPolling = () => {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  onUnmounted(() => stopPolling())

  return {
    count,
    loading,
    fetchCount,
    startPolling,
    stopPolling,
  }
}

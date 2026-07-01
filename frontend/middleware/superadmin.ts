export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore()

  if (!auth.isAuthenticated || !auth.token) {
    return navigateTo('/login?redirect=' + encodeURIComponent(to.fullPath))
  }

  const reportEvent = (eventType: string, severity?: string) => {
    if (!import.meta.client) return
    try {
      const api = useApi()
      api.post('/superadmin/audit/logs', {
        event_type: eventType,
        path: to.fullPath,
        severity,
      }).catch(() => {})
    } catch {
      // Best-effort: do not block navigation on logging failure
    }
  }

  if (auth.user?.role !== 'super_admin') {
    reportEvent('superadmin_access_denied', 'warning')
    return navigateTo('/')
  }

  reportEvent('superadmin_access_granted', 'info')
})

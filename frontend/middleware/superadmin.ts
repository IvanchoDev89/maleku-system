/**
 * Super Admin Middleware
 * Restricts access to /superadmin/* routes to SUPER_ADMIN role only.
 * Logs access attempts (granted and denied) to the backend audit log.
 */
export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore()

  if (!auth.isAuthenticated || !auth.token) {
    return navigateTo('/login?redirect=' + encodeURIComponent(to.fullPath))
  }

  const config = useRuntimeConfig()
  const apiBase = (config.public.apiBase as string).replace(/\/$/, '')
  const headers: Record<string, string> = {}
  if (auth.token) headers.Authorization = `Bearer ${auth.token}`

  const reportEvent = (eventType: string, severity?: string) => {
    if (!import.meta.client) return
    $fetch(`${apiBase}/superadmin/audit/logs`, {
      method: 'POST',
      headers,
      body: {
        event_type: eventType,
        path: to.fullPath,
        severity,
      },
    }).catch(() => {
      // Best-effort: do not block navigation on logging failure
    })
  }

  if (auth.user?.role !== 'super_admin') {
    reportEvent('superadmin_access_denied', 'warning')
    return navigateTo('/')
  }

  reportEvent('superadmin_access_granted', 'info')
})

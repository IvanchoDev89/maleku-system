import type { Ref } from 'vue'
import { useI18n } from 'vue-i18n'

const iconMap: Record<string, { name: string; bg: string }> = {
  user_created: { name: 'lucide:user-plus', bg: 'bg-green-100 text-green-600' },
  user_updated: { name: 'lucide:user-cog', bg: 'bg-blue-100 text-blue-600' },
  user_login: { name: 'lucide:log-in', bg: 'bg-purple-100 text-purple-600' },
  booking_created: { name: 'lucide:calendar-plus', bg: 'bg-orange-100 text-orange-600' },
  booking_confirmed: { name: 'lucide:check-circle', bg: 'bg-green-100 text-green-600' },
  vendor_created: { name: 'lucide:store', bg: 'bg-teal-100 text-teal-600' },
  vendor_verified: { name: 'lucide:shield-check', bg: 'bg-green-100 text-green-600' },
  content_created: { name: 'lucide:file-text', bg: 'bg-blue-100 text-blue-600' },
  security_alert: { name: 'lucide:alert-triangle', bg: 'bg-red-100 text-red-600' },
  default: { name: 'lucide:activity', bg: 'bg-gray-100 text-gray-600' },
}

export function formatNumber(num: number): string {
  if (!num) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

export function formatTimeAgo(timestamp: string): string {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000)
  if (diff < 60) return 'hace un momento'
  if (diff < 3600) return `hace ${Math.floor(diff / 60)} minutos`
  if (diff < 86400) return `hace ${Math.floor(diff / 3600)} horas`
  return `hace ${Math.floor(diff / 86400)} días`
}

export function useDashboard(revenuePeriod: Ref<string>) {
  const api = useApi()
  const { t } = useI18n()

  const stats = ref({
    total_users: 0,
    total_vendors: 0,
    total_bookings: 0,
    total_revenue: 0,
    net_revenue: 0,
    pending_vendors: 0,
    new_users_today: 0,
    active_users_today: 0,
  })

  const alerts = ref<any[]>([])
  const topVendors = ref<any[]>([])
  const recentActivity = ref<any[]>([])
  const securityStats = ref({ failed_logins_24h: 0, critical_events_24h: 0 })
  const loading = ref(false)
  const revenueData = ref<any[]>([])

  const loadDashboardData = async () => {
    loading.value = true
    try {
      const [dashboardStats, vendorsData, alertsData, revenueResult, activityData, auditSummary] = await Promise.all([
        api.get('/superadmin/dashboard/stats'),
        api.get('/superadmin/dashboard/top-vendors'),
        api.get('/superadmin/dashboard/alerts'),
        api.get(`/superadmin/dashboard/revenue-trend?days=${revenuePeriod.value}`),
        api.get('/superadmin/dashboard/recent-activity'),
        api.get('/superadmin/audit/summary'),
      ])

      stats.value = {
        total_users: dashboardStats.total_users,
        total_vendors: dashboardStats.total_vendors,
        total_bookings: dashboardStats.total_bookings,
        total_revenue: dashboardStats.total_revenue,
        net_revenue: dashboardStats.net_revenue,
        pending_vendors: dashboardStats.pending_vendors,
        new_users_today: dashboardStats.new_users_today,
        active_users_today: dashboardStats.active_users_today,
      }

      topVendors.value = vendorsData
      alerts.value = alertsData

      revenueData.value = revenueResult.data || revenueResult

      recentActivity.value = activityData.map((item: any) => {
        const iconConfig = iconMap[item.type] || iconMap.default
        return {
          id: item.id,
          title: item.user_name || item.title || 'Actividad',
          description: item.description,
          timestamp: item.timestamp,
          iconName: iconConfig.name,
          iconBg: iconConfig.bg,
          link: item.link || null,
        }
      })

      securityStats.value = {
        failed_logins_24h: auditSummary.failed_logins_24h,
        critical_events_24h: auditSummary.critical_events_24h,
      }
    } catch (error) {
      console.error('Error loading dashboard:', error)
      useToast().add(t('errors.dashboard.load'), 'error')
    } finally {
      loading.value = false
    }
  }

  const dismissAlert = async (alertId: string) => {
    try {
      await api.post(`/superadmin/dashboard/alerts/${alertId}/dismiss`)
    } catch (error) {
      console.error('Error dismissing alert:', error)
      useToast().add(t('errors.dashboard.dismiss'), 'error')
    }
    alerts.value = alerts.value.filter(a => a.id !== alertId)
  }

  return {
    stats,
    alerts,
    topVendors,
    recentActivity,
    securityStats,
    loading,
    revenueData,
    loadDashboardData,
    dismissAlert,
  }
}

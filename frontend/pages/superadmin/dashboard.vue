<template>
  <div class="space-y-6">
    <!-- Welcome Banner with System Status -->
    <div class="bg-gradient-to-r from-primary-900 via-primary-800 to-primary-900 rounded-2xl p-6 text-white border border-primary-700">
      <div class="flex justify-between items-start">
        <div>
          <h1 class="text-2xl font-bold flex items-center gap-2">
            {{ $t('superadmin.dashboard.welcome', { name: auth.user?.full_name?.split(' ')[0] }) }}
            <Crown class="w-6 h-6 text-primary-300" />
          </h1>
          <p class="text-primary-200 mt-1">{{ $t('superadmin.dashboard.subtitle') }}</p>
          <div class="flex items-center gap-3 mt-4">
            <div class="flex items-center gap-2 px-3 py-1.5 bg-green-500/20 rounded-lg border border-green-500/30">
              <CheckCircle class="w-4 h-4 text-green-400" />
              <span class="text-sm text-green-400 font-medium">{{ $t('superadmin.dashboard.system.operational') }}</span>
            </div>
            <div class="flex items-center gap-2 px-3 py-1.5 bg-blue-500/20 rounded-lg border border-blue-500/30">
              <Database class="w-4 h-4 text-blue-400" />
              <span class="text-sm text-blue-400 font-medium">{{ $t('superadmin.dashboard.system.dbConnected') }}</span>
            </div>
            <div class="flex items-center gap-2 px-3 py-1.5 bg-primary-500/20 rounded-lg border border-primary-500/30">
              <Save class="w-4 h-4 text-primary-300" />
              <span class="text-sm text-primary-300 font-medium">{{ $t('superadmin.dashboard.system.backup') }}</span>
            </div>
          </div>
        </div>
        <div class="text-right">
          <p class="text-sm text-primary-300">{{ currentDate }}</p>
          <div class="flex items-center gap-3 justify-end">
            <p class="text-3xl font-bold text-primary-300">{{ currentTime }}</p>
            <button
              @click="refreshDashboard"
              class="p-2 bg-primary-800 hover:bg-primary-700 rounded-lg transition-colors"
              :title="$t('superadmin.dashboard.refresh')"
            >
              <RefreshCw class="w-5 h-5 text-primary-100" :class="{ 'animate-spin': loading }" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Critical Alerts -->
    <div v-if="alerts.length > 0" class="space-y-3">
      <div
        v-for="alert in alerts"
        :key="alert.id"
        class="p-4 rounded-xl border-l-4 flex items-start justify-between shadow-sm"
        :class="{
          'bg-red-50 border-red-500': alert.severity === 'critical',
          'bg-orange-50 border-orange-500': alert.severity === 'warning',
          'bg-blue-50 border-blue-500': alert.severity === 'info'
        }"
      >
        <div class="flex items-start gap-3">
          <div
            class="w-10 h-10 rounded-full flex items-center justify-center"
            :class="{
              'bg-red-100 text-red-600': alert.severity === 'critical',
              'bg-orange-100 text-orange-600': alert.severity === 'warning',
              'bg-blue-100 text-blue-600': alert.severity === 'info'
            }"
          >
            <component
              :is="alert.severity === 'critical' ? AlertTriangle : alert.severity === 'warning' ? AlertCircle : Info"
              class="w-5 h-5"
            />
          </div>
          <div>
            <h3
              class="font-bold"
              :class="{
                'text-red-700': alert.severity === 'critical',
                'text-orange-700': alert.severity === 'warning',
                'text-blue-700': alert.severity === 'info'
              }"
            >
              {{ alert.title }}
            </h3>
            <p class="text-sm text-gray-600 mt-1">{{ alert.description }}</p>
            <p v-if="alert.timestamp" class="text-xs text-gray-400 mt-1 flex items-center gap-1">
              <Clock class="w-3 h-3" />
              {{ formatTimeAgo(alert.timestamp) }}
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <NuxtLink
            v-if="alert.entity_type"
            :to="`/superadmin/${alert.entity_type}s`"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1"
            :class="{
              'bg-red-500 hover:bg-red-600 text-white': alert.severity === 'critical',
              'bg-orange-500 hover:bg-orange-600 text-white': alert.severity === 'warning',
              'bg-blue-500 hover:bg-blue-600 text-white': alert.severity === 'info'
            }"
          >
            <Eye class="w-4 h-4" />
            Ver
          </NuxtLink>
          <button
            @click="dismissAlert(alert.id)"
            class="p-2 rounded-lg transition-colors"
            :class="{
              'hover:bg-red-100 text-red-400': alert.severity === 'critical',
              'hover:bg-orange-100 text-orange-400': alert.severity === 'warning',
              'hover:bg-blue-100 text-blue-400': alert.severity === 'info'
            }"
            title="Descartar alerta"
          >
            <X class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <UiCard
        v-for="(stat, index) in statsCards"
        :key="index"
        padding="sm"
        hover
        class="cursor-pointer"
        @click="navigateTo(stat.link)"
      >
        <div v-if="loading && !stats.total_users" class="animate-pulse space-y-3">
          <div class="h-4 bg-gray-200 rounded w-24" />
          <div class="h-8 bg-gray-200 rounded w-32" />
          <div class="h-3 bg-gray-200 rounded w-20" />
        </div>
        <div v-else class="flex items-start justify-between">
          <div>
            <p class="text-gray-500 text-sm font-medium">{{ stat.label }}</p>
            <p class="text-2xl font-bold text-gray-900 mt-1">{{ stat.value }}</p>
            <div class="flex items-center gap-1 mt-2">
              <span :class="stat.trend > 0 ? 'text-green-500' : 'text-red-500'" class="text-sm font-medium">
                {{ stat.trend > 0 ? '↑' : stat.trend < 0 ? '↓' : '→' }} {{ Math.abs(stat.trend) }}%
              </span>
              <span class="text-gray-400 text-xs">vs mes anterior</span>
            </div>
          </div>
          <div :class="`w-12 h-12 rounded-xl flex items-center justify-center ${stat.iconBg}`">
            <component :is="stat.icon" class="w-6 h-6" :class="stat.iconColor" />
          </div>
        </div>
      </UiCard>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Revenue Chart -->
      <UiCard padding="md" class="lg:col-span-2">
        <div class="flex justify-between items-center mb-6">
          <div>
            <h3 class="text-lg font-bold text-gray-900">Ingresos y Tendencias</h3>
            <p class="text-gray-500 text-sm">Últimos {{ revenuePeriod }} días</p>
          </div>
          <div class="flex gap-2">
            <button
              v-for="period in ['7', '30', '90']"
              :key="period"
              @click="revenuePeriod = period"
              :class="revenuePeriod === period ? 'bg-primary-600 text-white shadow-sm' : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'"
              class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
            >
              {{ period === '7' ? '7D' : period === '30' ? '30D' : '90D' }}
            </button>
          </div>
        </div>
        <div class="h-72">
          <div v-if="loading && revenueData.length === 0" class="h-full flex items-center justify-center">
            <div class="animate-pulse space-y-4 w-full px-8">
              <div class="h-4 bg-gray-200 rounded w-1/4" />
              <div class="h-48 bg-gray-100 rounded-lg" />
            </div>
          </div>
          <canvas v-else ref="revenueChartRef"></canvas>
        </div>
      </UiCard>

      <!-- System Health -->
      <UiCard padding="md">
        <h3 class="text-lg font-bold text-gray-900 mb-4">Salud del Sistema</h3>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-3 bg-green-50 rounded-lg">
            <div class="flex items-center gap-3">
              <span class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
              <span class="font-medium text-gray-700">API Server</span>
            </div>
            <span class="text-green-600 font-medium text-sm">Operativo</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-green-50 rounded-lg">
            <div class="flex items-center gap-3">
              <span class="w-3 h-3 bg-green-500 rounded-full"></span>
              <span class="font-medium text-gray-700">Base de Datos</span>
            </div>
            <span class="text-green-600 font-medium text-sm">Conectado</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-green-50 rounded-lg">
            <div class="flex items-center gap-3">
              <span class="w-3 h-3 bg-green-500 rounded-full"></span>
              <span class="font-medium text-gray-700">Frontend</span>
            </div>
            <span class="text-green-600 font-medium text-sm">Activo</span>
          </div>

          <div class="mt-4 p-4 bg-primary-50 rounded-lg">
            <div class="flex justify-between text-sm mb-1">
              <span class="text-gray-600">Usuarios nuevos (hoy)</span>
              <span class="font-bold text-primary-700">{{ stats.new_users_today || 0 }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">Vendors pendientes</span>
              <span class="font-bold text-amber-600">{{ stats.pending_vendors || 0 }}</span>
            </div>
          </div>
        </div>
      </UiCard>
    </div>

    <!-- Second Row -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Top Vendors -->
      <UiCard padding="md">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-gray-900 flex items-center gap-2">
            <Trophy class="w-5 h-5 text-primary-600" />
            Top Proveedores
          </h3>
          <NuxtLink to="/superadmin/vendors" class="text-primary-600 text-sm hover:underline flex items-center gap-1">
            Ver todos
            <ArrowRight class="w-4 h-4" />
          </NuxtLink>
        </div>
        <div v-if="loading && topVendors.length === 0" class="space-y-3">
          <div v-for="i in 5" :key="i" class="flex items-center gap-3 p-3 animate-pulse">
            <div class="w-10 h-10 bg-gray-200 rounded-full shrink-0" />
            <div class="flex-1 space-y-2">
              <div class="h-3 bg-gray-200 rounded w-3/4" />
              <div class="h-2 bg-gray-100 rounded w-1/2" />
            </div>
            <div class="h-4 bg-gray-200 rounded w-16" />
          </div>
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="(vendor, index) in topVendors.slice(0, 5)"
            :key="vendor.vendor_id"
            class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer group"
          >
            <div
              class="w-10 h-10 rounded-full flex items-center justify-center font-bold shadow-sm"
              :class="index === 0 ? 'bg-gradient-to-br from-yellow-300 to-yellow-500 text-yellow-900' : index === 1 ? 'bg-gradient-to-br from-gray-200 to-gray-400 text-gray-800' : index === 2 ? 'bg-gradient-to-br from-amber-400 to-amber-600 text-white' : 'bg-gray-200 text-gray-600'"
            >
              <span v-if="index < 3">{{ index + 1 }}</span>
              <Store v-else class="w-4 h-4" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-gray-900 truncate group-hover:text-primary-700 transition-colors">{{ vendor.vendor_name }}</p>
              <p class="text-gray-500 text-xs flex items-center gap-1">
                <Calendar class="w-3 h-3" />
                {{ vendor.total_bookings }} reservas
              </p>
            </div>
            <div class="text-right">
              <p class="font-bold text-green-600">{{ formatCurrency(vendor.total_revenue) }}</p>
              <NuxtLink
                :to="`/superadmin/vendors/${vendor.vendor_id}`"
                class="text-xs text-primary-600 hover:text-primary-700 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                Ver →
              </NuxtLink>
            </div>
          </div>
          <p v-if="topVendors.length === 0" class="text-gray-400 text-center py-4 flex flex-col items-center">
            <Store class="w-8 h-8 mb-2 opacity-50" />
            No hay datos aún
          </p>
        </div>
      </UiCard>

      <!-- Recent Activity -->
      <UiCard padding="md">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-gray-900">Actividad Reciente</h3>
          <NuxtLink to="/superadmin/audit" class="text-primary-600 text-sm hover:underline">Ver logs →</NuxtLink>
        </div>
        <div v-if="loading && recentActivity.length === 0" class="space-y-3">
          <div v-for="i in 5" :key="i" class="flex items-start gap-3 p-3 animate-pulse">
            <div class="w-10 h-10 bg-gray-200 rounded-full shrink-0" />
            <div class="flex-1 space-y-2">
              <div class="h-3 bg-gray-200 rounded w-3/4" />
              <div class="h-2 bg-gray-100 rounded w-full" />
              <div class="h-2 bg-gray-100 rounded w-1/4" />
            </div>
          </div>
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="activity in recentActivity"
            :key="activity.id"
            class="flex items-start gap-3 p-3 border-b border-gray-100 last:border-0 hover:bg-gray-50 rounded-lg transition-colors cursor-pointer"
          >
            <div class="w-10 h-10 rounded-full flex items-center justify-center" :class="activity.iconBg">
              <component :is="activity.iconName === 'lucide:user' ? User : activity.iconName === 'lucide:store' ? Store : activity.iconName === 'lucide:check-circle' ? CheckCircle : activity.iconName === 'lucide:file-text' ? FileText : Activity" class="w-5 h-5" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">{{ activity.title }}</p>
              <p class="text-xs text-gray-500 line-clamp-1">{{ activity.description }}</p>
              <p class="text-xs text-gray-400 mt-1 flex items-center gap-1">
                <Clock class="w-3 h-3" />
                {{ formatTimeAgo(activity.timestamp) }}
              </p>
            </div>
            <NuxtLink v-if="activity.link" :to="activity.link" class="text-primary-600 hover:text-primary-700">
              <ChevronRight class="w-5 h-5" />
            </NuxtLink>
          </div>
          <p v-if="recentActivity.length === 0" class="text-gray-400 text-center py-4 flex flex-col items-center">
            <Inbox class="w-8 h-8 mb-2 opacity-50" />
            No hay actividad reciente
          </p>
        </div>
      </UiCard>

      <!-- Quick Actions & Security -->
      <UiCard padding="md">
        <h3 class="text-lg font-bold text-gray-900 mb-4">Acciones Rápidas</h3>
        <div class="grid grid-cols-2 gap-3 mb-6">
          <NuxtLink to="/superadmin/users" class="p-4 bg-primary-50 rounded-xl hover:bg-primary-100 transition-colors text-center group border border-primary-100">
            <UserPlus class="w-8 h-8 mx-auto mb-2 text-primary-600 group-hover:scale-110 transition-transform" />
            <p class="font-medium text-gray-700 text-sm">Nuevo Usuario</p>
          </NuxtLink>
          <NuxtLink to="/superadmin/vendors/pending" class="p-4 bg-primary-50 rounded-xl hover:bg-primary-100 transition-colors text-center group border border-primary-100">
            <CheckCircle class="w-8 h-8 mx-auto mb-2 text-green-600 group-hover:scale-110 transition-transform" />
            <p class="font-medium text-gray-700 text-sm">Aprobar Vendor</p>
          </NuxtLink>
          <NuxtLink to="/superadmin/content/blog" class="p-4 bg-primary-50 rounded-xl hover:bg-primary-100 transition-colors text-center group border border-primary-100">
            <FileText class="w-8 h-8 mx-auto mb-2 text-blue-600 group-hover:scale-110 transition-transform" />
            <p class="font-medium text-gray-700 text-sm">Blog Post</p>
          </NuxtLink>
          <NuxtLink to="/superadmin/system" class="p-4 bg-primary-50 rounded-xl hover:bg-primary-100 transition-colors text-center group border border-primary-100">
            <Settings class="w-8 h-8 mx-auto mb-2 text-purple-600 group-hover:scale-110 transition-transform" />
            <p class="font-medium text-gray-700 text-sm">Sistema</p>
          </NuxtLink>
        </div>

        <h4 class="font-bold text-gray-900 mb-3 flex items-center gap-2">
          <ShieldCheck class="w-5 h-5 text-green-600" />
          Seguridad
        </h4>
        <div class="space-y-2">
          <div class="flex justify-between items-center p-3 rounded-lg border" :class="(securityStats.failed_logins_24h || 0) > 20 ? 'bg-red-50 border-red-100' : 'bg-amber-50 border-amber-100'">
            <div class="flex items-center gap-2">
              <UserX class="w-4 h-4" :class="(securityStats.failed_logins_24h || 0) > 20 ? 'text-red-600' : 'text-amber-600'" />
              <span class="text-sm" :class="(securityStats.failed_logins_24h || 0) > 20 ? 'text-red-700' : 'text-amber-700'">Intentos fallidos (24h)</span>
            </div>
            <span class="font-bold" :class="(securityStats.failed_logins_24h || 0) > 20 ? 'text-red-600' : 'text-amber-600'">{{ securityStats.failed_logins_24h || 0 }}</span>
          </div>
          <div class="flex justify-between items-center p-3 rounded-lg border" :class="(securityStats.critical_events_24h || 0) > 5 ? 'bg-red-50 border-red-100' : 'bg-red-50 border-red-100'">
            <div class="flex items-center gap-2">
              <AlertCircle class="w-4 h-4 text-red-600" />
              <span class="text-sm text-red-700">Eventos críticos (24h)</span>
            </div>
            <span class="font-bold text-red-600">{{ securityStats.critical_events_24h || 0 }}</span>
          </div>
          <div class="flex justify-between items-center p-3 bg-blue-50 rounded-lg border border-blue-100">
            <div class="flex items-center gap-2">
              <Activity class="w-4 h-4 text-blue-600" />
              <span class="text-sm text-blue-700">Usuarios activos</span>
            </div>
            <span class="font-bold text-blue-600">{{ stats.active_users_today || 0 }}</span>
          </div>
        </div>
      </UiCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Chart, registerables } from 'chart.js'
import {
  Crown, CheckCircle, Database, Save, RefreshCw, AlertTriangle, AlertCircle,
  Info, Clock, Eye, X, Trophy, ArrowRight, Store, Calendar, Activity,
  ChevronRight, Inbox, UserPlus, FileText, Settings, ShieldCheck, UserX, User,
  Users, Building2, CalendarCheck, DollarSign,
} from 'lucide-vue-next'

Chart.register(...registerables)

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const auth = useAuthStore()

const revenuePeriod = ref('30')
const revenueChartRef = ref<HTMLCanvasElement | null>(null)
let revenueChart: Chart | null = null

const { stats, alerts, topVendors, recentActivity, securityStats, loading, revenueData, loadDashboardData, dismissAlert } = useDashboard(revenuePeriod)

const currentDate = computed(() => new Date().toLocaleDateString('es-CR', {
  weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
}))

const currentTime = computed(() => new Date().toLocaleTimeString('es-CR', {
  hour: '2-digit', minute: '2-digit'
}))

const statsCards = computed(() => [
  { label: 'Usuarios Totales', value: formatNumber(stats.value.total_users), icon: Users, iconBg: 'bg-primary-100', iconColor: 'text-primary-600', trend: 12, link: '/superadmin/users' },
  { label: 'Proveedores', value: formatNumber(stats.value.total_vendors), icon: Store, iconBg: 'bg-primary-100', iconColor: 'text-primary-600', trend: 8, link: '/superadmin/vendors' },
  { label: 'Reservas', value: formatNumber(stats.value.total_bookings), icon: CalendarCheck, iconBg: 'bg-primary-100', iconColor: 'text-primary-600', trend: -3, link: '/superadmin/bookings' },
  { label: 'Ingresos Netos', value: formatCurrency(stats.value.net_revenue), icon: DollarSign, iconBg: 'bg-green-100', iconColor: 'text-green-600', trend: 15, link: '/superadmin/reports' },
])

function buildRevenueChart() {
  const data = revenueData.value
  if (revenueChart) revenueChart.destroy()
  if (!revenueChartRef.value || !data.length) return

  const maxBookings = Math.max(...data.map((r: any) => r.bookings_count || 0), 1)
  const bookingScaleFactor = maxBookings > 0 ? Math.ceil(Math.max(...data.map((r: any) => r.revenue || 0)) / maxBookings / 10) * 10 : 100

  revenueChart = new Chart(revenueChartRef.value, {
    type: 'line',
    data: {
      labels: data.map((r: any) => r.date.slice(5)),
      datasets: [
        {
          label: 'Ingresos',
          data: data.map((r: any) => r.revenue),
          borderColor: '#0d9488',
          backgroundColor: 'rgba(13, 148, 136, 0.1)',
          borderWidth: 2, fill: true, tension: 0.4,
          pointRadius: 3, pointBackgroundColor: '#0d9488',
          yAxisID: 'y',
        },
        {
          label: 'Reservas',
          data: data.map((r: any) => (r.bookings_count || 0) * bookingScaleFactor),
          borderColor: '#3b82f6',
          backgroundColor: 'transparent',
          borderWidth: 2, borderDash: [5, 5], tension: 0.4,
          pointRadius: 3, pointBackgroundColor: '#3b82f6',
          yAxisID: 'y1',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top', labels: { usePointStyle: true, padding: 20 } },
        tooltip: {
          callbacks: {
            label(context: any) {
              const label = context.dataset.label || ''
              if (context.dataset.label === 'Reservas') {
                const raw = (context.parsed.y / bookingScaleFactor)
                return `${label}: ${raw}`
              }
              return `${label}: $${context.parsed.y.toLocaleString()}`
            },
          },
        },
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#6b7280', maxTicksLimit: 8 } },
        y: {
          grid: { color: '#e5e7eb' },
          ticks: {
            color: '#6b7280',
            callback: (v: any) => '$' + Math.round(v / 1000) + 'K',
          },
        },
        y1: {
          position: 'right',
          grid: { display: false },
          ticks: {
            color: '#3b82f6',
            callback: (v: any) => Math.round(v / bookingScaleFactor).toString(),
          },
          min: 0,
        },
      },
    },
  })
}

watch(revenueData, buildRevenueChart)
watch(revenuePeriod, loadDashboardData)

const refreshDashboard = loadDashboardData

onMounted(loadDashboardData)

onUnmounted(() => {
  revenueChart?.destroy()
})
</script>

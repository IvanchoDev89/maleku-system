<template>
  <div class="space-y-6">
    <!-- Welcome Banner with System Status -->
    <div class="bg-gradient-to-r from-teal-900 via-teal-800 to-teal-900 rounded-2xl p-6 text-white border border-teal-700">
      <div class="flex justify-between items-start">
        <div>
          <h1 class="text-2xl font-bold flex items-center gap-2">
            {{ $t('superadmin.dashboard.welcome', { name: auth.user?.full_name?.split(' ')[0] }) }}
            <Crown class="w-6 h-6 text-teal-300" />
          </h1>
          <p class="text-teal-200 mt-1">{{ $t('superadmin.dashboard.subtitle') }}</p>
          <div class="flex items-center gap-3 mt-4">
            <div class="flex items-center gap-2 px-3 py-1.5 bg-green-500/20 rounded-lg border border-green-500/30">
              <CheckCircle class="w-4 h-4 text-green-400" />
              <span class="text-sm text-green-400 font-medium">{{ $t('superadmin.dashboard.system.operational') }}</span>
            </div>
            <div class="flex items-center gap-2 px-3 py-1.5 bg-blue-500/20 rounded-lg border border-blue-500/30">
              <Database class="w-4 h-4 text-blue-400" />
              <span class="text-sm text-blue-400 font-medium">{{ $t('superadmin.dashboard.system.dbConnected') }}</span>
            </div>
            <div class="flex items-center gap-2 px-3 py-1.5 bg-teal-500/20 rounded-lg border border-teal-500/30">
              <Save class="w-4 h-4 text-teal-300" />
              <span class="text-sm text-teal-300 font-medium">{{ $t('superadmin.dashboard.system.backup') }}</span>
            </div>
          </div>
        </div>
        <div class="text-right">
          <p class="text-sm text-teal-300">{{ currentDate }}</p>
          <div class="flex items-center gap-3 justify-end">
            <p class="text-3xl font-bold text-teal-300">{{ currentTime }}</p>
            <button 
              @click="refreshDashboard"
              class="p-2 bg-teal-800 hover:bg-teal-700 rounded-lg transition-colors"
              :title="$t('superadmin.dashboard.refresh')"
            >
              <RefreshCw class="w-5 h-5 text-teal-100" :class="{ 'animate-spin': loading }" />
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
      <div 
        v-for="(stat, index) in statsCards" 
        :key="index" 
        class="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow cursor-pointer"
        @click="navigateTo(stat.link)"
      >
        <div class="flex items-start justify-between">
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
          <div :class="`w-12 h-12 rounded-xl flex items-center justify-center ${stat.bgClass}`">
            <span class="text-2xl">{{ stat.icon }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Revenue Chart -->
      <div class="lg:col-span-2 bg-white rounded-xl p-6 shadow-sm border border-gray-100">
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
              :class="revenuePeriod === period ? 'bg-teal-600 text-white' : 'bg-teal-50 text-teal-700 hover:bg-teal-100'"
              class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
            >
              {{ period === '7' ? '7D' : period === '30' ? '30D' : '90D' }}
            </button>
          </div>
        </div>
        <div class="h-72">
          <canvas ref="revenueChartRef"></canvas>
        </div>
      </div>

      <!-- System Health -->
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
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
          
          <div class="mt-4 p-4 bg-teal-50 rounded-lg">
            <div class="flex justify-between text-sm mb-2">
              <span class="text-gray-600">Uso de memoria</span>
              <span class="font-medium text-gray-700">256 MB / 512 MB</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-teal-600 h-2 rounded-full" style="width: 50%"></div>
            </div>
          </div>
          
          <div class="p-4 bg-teal-50 rounded-lg">
            <div class="flex justify-between text-sm mb-2">
              <span class="text-gray-600">Almacenamiento DB</span>
              <span class="font-medium text-gray-700">1.2 GB / 10 GB</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-teal-600 h-2 rounded-full" style="width: 12%"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Second Row -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Top Vendors -->
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-gray-900 flex items-center gap-2">
            <Trophy class="w-5 h-5 text-teal-600" />
            Top Proveedores
          </h3>
          <NuxtLink to="/superadmin/vendors" class="text-teal-600 text-sm hover:underline flex items-center gap-1">
            Ver todos
            <ArrowRight class="w-4 h-4" />
          </NuxtLink>
        </div>
        <div class="space-y-3">
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
              <p class="font-medium text-gray-900 truncate group-hover:text-teal-700 transition-colors">{{ vendor.vendor_name }}</p>
              <p class="text-gray-500 text-xs flex items-center gap-1">
                <Calendar class="w-3 h-3" />
                {{ vendor.total_bookings }} reservas
              </p>
            </div>
            <div class="text-right">
              <p class="font-bold text-green-600">${{ formatNumber(vendor.total_revenue) }}</p>
              <NuxtLink 
                :to="`/superadmin/vendors/${vendor.vendor_id}`" 
                class="text-xs text-teal-600 hover:text-teal-700 opacity-0 group-hover:opacity-100 transition-opacity"
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
      </div>

      <!-- Recent Activity -->
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-gray-900">Actividad Reciente</h3>
          <NuxtLink to="/superadmin/audit" class="text-teal-600 text-sm hover:underline">Ver logs →</NuxtLink>
        </div>
        <div class="space-y-3">
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
            <NuxtLink v-if="activity.link" :to="activity.link" class="text-teal-600 hover:text-teal-700">
              <ChevronRight class="w-5 h-5" />
            </NuxtLink>
          </div>
          <p v-if="recentActivity.length === 0" class="text-gray-400 text-center py-4 flex flex-col items-center">
            <Inbox class="w-8 h-8 mb-2 opacity-50" />
            No hay actividad reciente
          </p>
        </div>
      </div>

      <!-- Quick Actions & Security -->
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 class="text-lg font-bold text-gray-900 mb-4">Acciones Rápidas</h3>
        <div class="grid grid-cols-2 gap-3 mb-6">
          <NuxtLink to="/superadmin/users" class="p-4 bg-teal-50 rounded-xl hover:bg-teal-100 transition-colors text-center group border border-teal-100">
            <UserPlus class="w-8 h-8 mx-auto mb-2 text-teal-600 group-hover:scale-110 transition-transform" />
            <p class="font-medium text-gray-700 text-sm">Nuevo Usuario</p>
          </NuxtLink>
          <NuxtLink to="/superadmin/vendors/pending" class="p-4 bg-teal-50 rounded-xl hover:bg-teal-100 transition-colors text-center group border border-teal-100">
            <CheckCircle class="w-8 h-8 mx-auto mb-2 text-green-600 group-hover:scale-110 transition-transform" />
            <p class="font-medium text-gray-700 text-sm">Aprobar Vendor</p>
          </NuxtLink>
          <NuxtLink to="/superadmin/content/blog/new" class="p-4 bg-teal-50 rounded-xl hover:bg-teal-100 transition-colors text-center group border border-teal-100">
            <FileText class="w-8 h-8 mx-auto mb-2 text-blue-600 group-hover:scale-110 transition-transform" />
            <p class="font-medium text-gray-700 text-sm">Blog Post</p>
          </NuxtLink>
          <NuxtLink to="/superadmin/system" class="p-4 bg-teal-50 rounded-xl hover:bg-teal-100 transition-colors text-center group border border-teal-100">
            <Settings class="w-8 h-8 mx-auto mb-2 text-purple-600 group-hover:scale-110 transition-transform" />
            <p class="font-medium text-gray-700 text-sm">Sistema</p>
          </NuxtLink>
        </div>

        <h4 class="font-bold text-gray-900 mb-3 flex items-center gap-2">
          <ShieldCheck class="w-5 h-5 text-green-600" />
          Seguridad
        </h4>
        <div class="space-y-2">
          <div class="flex justify-between items-center p-3 bg-green-50 rounded-lg border border-green-100">
            <div class="flex items-center gap-2">
              <UserX class="w-4 h-4 text-green-600" />
              <span class="text-sm text-gray-600">Intentos fallidos (24h)</span>
            </div>
            <span class="font-bold text-green-600">{{ securityStats.failed_logins_24h || 0 }}</span>
          </div>
          <div class="flex justify-between items-center p-3 bg-green-50 rounded-lg border border-green-100">
            <div class="flex items-center gap-2">
              <AlertCircle class="w-4 h-4 text-green-600" />
              <span class="text-sm text-gray-600">Eventos críticos (24h)</span>
            </div>
            <span class="font-bold text-green-600">{{ securityStats.critical_events_24h || 0 }}</span>
          </div>
          <div class="flex justify-between items-center p-3 bg-blue-50 rounded-lg border border-blue-100">
            <div class="flex items-center gap-2">
              <Activity class="w-4 h-4 text-blue-600" />
              <span class="text-sm text-gray-600">Usuarios activos</span>
            </div>
            <span class="font-bold text-blue-600">{{ stats.active_users_today || 0 }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Chart, registerables } from 'chart.js'
import { Crown, CheckCircle, Database, Save, RefreshCw, AlertTriangle, AlertCircle, Info, Clock, Eye, X, Trophy, ArrowRight, Store, Calendar, Activity, ChevronRight, Inbox, UserPlus, FileText, Settings, ShieldCheck, UserX, User } from 'lucide-vue-next'

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
  { label: 'Usuarios Totales', value: formatNumber(stats.value.total_users), icon: '👥', bgClass: 'bg-teal-100', trend: 12, link: '/superadmin/users' },
  { label: 'Proveedores', value: formatNumber(stats.value.total_vendors), icon: '🏪', bgClass: 'bg-teal-100', trend: 8, link: '/superadmin/vendors' },
  { label: 'Reservas', value: formatNumber(stats.value.total_bookings), icon: '📋', bgClass: 'bg-teal-100', trend: -3, link: '/superadmin/bookings' },
  { label: 'Ingresos Netos', value: `$${formatNumber(stats.value.net_revenue)}`, icon: '💰', bgClass: 'bg-green-100', trend: 15, link: '/superadmin/reports' },
])

function buildRevenueChart() {
  const data = revenueData.value
  if (revenueChart) revenueChart.destroy()
  if (!revenueChartRef.value || !data.length) return

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
        },
        {
          label: 'Reservas',
          data: data.map((r: any) => r.bookings_count * 100),
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
              if (context.dataset.label === 'Reservas') return `${label}: ${Math.round(context.parsed.y / 100)}`
              return `${label}: $${context.parsed.y.toLocaleString()}`
            },
          },
        },
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#6b7280', maxTicksLimit: 8 } },
        y: { grid: { color: '#e5e7eb' }, ticks: { color: '#6b7280', callback: (v: any) => '$' + (v / 1000) + 'K' } },
        y1: { position: 'right', grid: { display: false }, ticks: { display: false }, min: 0 },
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

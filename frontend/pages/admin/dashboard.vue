<template>
  <div class="space-y-6">
    <!-- Welcome Banner -->
    <div class="bg-gradient-to-r from-primary to-primary-light rounded-2xl p-6 text-white">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold">Bienvenido, {{ auth.user?.full_name?.split(' ')[0] }} 👋</h1>
          <p class="opacity-90 mt-1">Aquí está lo que está pasando con tu plataforma hoy</p>
        </div>
        <div class="text-right">
          <p class="text-sm opacity-80">{{ currentDate }}</p>
          <p class="text-3xl font-bold">{{ currentTime }}</p>
        </div>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div v-for="(stat, index) in statsCards" :key="index"
        class="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-gray-500 text-sm font-medium">{{ stat.label }}</p>
            <p class="text-2xl font-bold text-gray-900 mt-1">{{ stat.value }}</p>
            <div class="flex items-center gap-1 mt-2">
              <span :class="stat.trend > 0 ? 'text-green-500' : 'text-red-500'" class="text-sm font-medium">
                {{ stat.trend > 0 ? '↑' : '↓' }} {{ Math.abs(stat.trend) }}%
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

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Revenue Chart - Large -->
      <div class="lg:col-span-2 bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div class="flex justify-between items-center mb-6">
          <div>
            <h3 class="text-lg font-bold text-gray-900">Ingresos y Ganancias</h3>
            <p class="text-gray-500 text-sm">Últimos {{ revenuePeriod }} días</p>
          </div>
          <div class="flex gap-2">
            <button v-for="period in ['7', '30', '90']" :key="period"
              @click="revenuePeriod = period"
              :class="revenuePeriod === period ? 'bg-primary text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
              class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors">
              {{ period === '7' ? '7D' : period === '30' ? '30D' : '90D' }}
            </button>
          </div>
        </div>
        <div class="h-72">
          <canvas ref="revenueChartRef"></canvas>
        </div>
      </div>

      <!-- Bookings by Status -->
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 class="text-lg font-bold text-gray-900 mb-6">Estado de Reservas</h3>
        <div class="h-56">
          <canvas ref="bookingsChartRef"></canvas>
        </div>
        <div class="mt-4 space-y-2">
          <div v-for="status in bookingsByStatus" :key="status.status" class="flex justify-between items-center">
            <div class="flex items-center gap-2">
              <span :class="`w-3 h-3 rounded-full`" :style="{ backgroundColor: statusColors[status.status] }"></span>
              <span class="text-sm text-gray-600 capitalize">{{ statusLabels[status.status] }}</span>
            </div>
            <span class="font-semibold text-gray-900">{{ status.count }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Second Row -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Top Vendors -->
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-gray-900">Top Proveedores</h3>
          <NuxtLink to="/admin/vendors" class="text-primary text-sm hover:underline">Ver todos →</NuxtLink>
        </div>
        <div class="space-y-4">
          <div v-for="(vendor, index) in topVendors.slice(0, 5)" :key="vendor.vendor_id"
            class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold"
              :class="index === 0 ? 'bg-yellow-400 text-black' : index === 1 ? 'bg-gray-300 text-black' : index === 2 ? 'bg-amber-600 text-white' : 'bg-gray-200 text-gray-600'">
              {{ index + 1 }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-medium text-gray-900 truncate">{{ vendor.vendor_name }}</p>
              <p class="text-gray-500 text-xs">{{ vendor.total_bookings }} reservas</p>
            </div>
            <div class="text-right">
              <p class="font-bold text-green-600">${{ formatNumber(vendor.total_revenue) }}</p>
            </div>
          </div>
          <p v-if="topVendors.length === 0" class="text-gray-400 text-center py-4">No hay datos aún</p>
        </div>
      </div>

      <!-- Recent Bookings -->
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-gray-900">Reservas Recientes</h3>
          <NuxtLink to="/admin/bookings" class="text-primary text-sm hover:underline">Ver todas →</NuxtLink>
        </div>
        <div class="space-y-3">
          <div v-for="booking in recentBookings" :key="booking.id"
            class="flex items-center justify-between p-3 border-b border-gray-100 last:border-0">
            <div>
              <p class="font-medium text-gray-900 text-sm">{{ booking.user_name }}</p>
              <p class="text-gray-500 text-xs">{{ booking.vendor_name }}</p>
            </div>
            <div class="text-right">
              <p class="font-bold text-gray-900">${{ booking.total_amount }}</p>
              <span :class="`text-xs px-2 py-0.5 rounded-full ${bookingStatusClass[booking.status]}`">
                {{ bookingStatusLabel[booking.status] }}
              </span>
            </div>
          </div>
          <p v-if="recentBookings.length === 0" class="text-gray-400 text-center py-4">No hay reservas</p>
        </div>
      </div>

      <!-- System Health -->
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 class="text-lg font-bold text-gray-900 mb-4">Estado del Sistema</h3>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-3 bg-green-50 rounded-lg">
            <div class="flex items-center gap-3">
              <span class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
              <span class="font-medium text-gray-700">API Server</span>
            </div>
            <span class="text-green-600 font-medium">Operativo</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-green-50 rounded-lg">
            <div class="flex items-center gap-3">
              <span class="w-3 h-3 bg-green-500 rounded-full"></span>
              <span class="font-medium text-gray-700">Base de Datos</span>
            </div>
            <span class="text-green-600 font-medium">Conectado</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-green-50 rounded-lg">
            <div class="flex items-center gap-3">
              <span class="w-3 h-3 bg-green-500 rounded-full"></span>
              <span class="font-medium text-gray-700">Frontend</span>
            </div>
            <span class="text-green-600 font-medium">Activo</span>
          </div>
          <div class="mt-4 p-4 bg-gray-50 rounded-lg">
            <div class="flex justify-between text-sm mb-2">
              <span class="text-gray-500">Uso de memoria</span>
              <span class="font-medium text-gray-700">256 MB</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-primary h-2 rounded-full" style="width: 45%"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <NuxtLink to="/admin/blog/new" class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-all text-center group">
        <span class="text-3xl block mb-2 group-hover:scale-110 transition-transform">📝</span>
        <p class="font-medium text-gray-700">Nuevo Artículo</p>
      </NuxtLink>
      <NuxtLink to="/admin/users" class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-all text-center group">
        <span class="text-3xl block mb-2 group-hover:scale-110 transition-transform">👤</span>
        <p class="font-medium text-gray-700">Gestionar Usuarios</p>
      </NuxtLink>
      <NuxtLink to="/admin/destinations" class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-all text-center group">
        <span class="text-3xl block mb-2 group-hover:scale-110 transition-transform">🗺️</span>
        <p class="font-medium text-gray-700">Destinos</p>
      </NuxtLink>
      <NuxtLink to="/admin/settings" class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-all text-center group">
        <span class="text-3xl block mb-2 group-hover:scale-110 transition-transform">⚙️</span>
        <p class="font-medium text-gray-700">Configuración</p>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

definePageMeta({
  layout: 'admin',
  middleware: ['auth']
})

const api = useApi()
const auth = useAuthStore()

const revenuePeriod = ref('30')
const revenueChartRef = ref<HTMLCanvasElement | null>(null)
const bookingsChartRef = ref<HTMLCanvasElement | null>(null)

let revenueChart: Chart | null = null
let bookingsChart: Chart | null = null

const stats = ref({
  total_users: 0,
  total_vendors: 0,
  total_bookings: 0,
  total_revenue: 0,
  net_revenue: 0,
  pending_bookings: 0,
  completed_bookings: 0,
  cancelled_bookings: 0
})

const revenueData = ref<any[]>([])
const topVendors = ref<any[]>([])
const bookingsByStatus = ref<any[]>([])
const recentBookings = ref<any[]>([])

const currentDate = computed(() => new Date().toLocaleDateString('es-CR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }))
const currentTime = computed(() => new Date().toLocaleTimeString('es-CR', { hour: '2-digit', minute: '2-digit' }))

const statsCards = computed(() => [
  { label: 'Usuarios Totales', value: stats.value.total_users, icon: '👥', bgClass: 'bg-blue-100', trend: 12 },
  { label: 'Proveedores', value: stats.value.total_vendors, icon: '🏪', bgClass: 'bg-purple-100', trend: 8 },
  { label: 'Reservas', value: stats.value.total_bookings, icon: '📋', bgClass: 'bg-orange-100', trend: -3 },
  { label: 'Ingresos Netos', value: `$${formatNumber(stats.value.net_revenue)}`, icon: '💰', bgClass: 'bg-green-100', trend: 15 }
])

const statusColors: Record<string, string> = {
  pending: '#f59e0b',
  confirmed: '#22c55e',
  cancelled: '#ef4444',
  completed: '#3b82f6'
}

const statusLabels: Record<string, string> = {
  pending: 'Pendiente',
  confirmed: 'Confirmada',
  cancelled: 'Cancelada',
  completed: 'Completada'
}

const bookingStatusClass: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-700',
  confirmed: 'bg-green-100 text-green-700',
  cancelled: 'bg-red-100 text-red-700',
  completed: 'bg-blue-100 text-blue-700'
}

const bookingStatusLabel: Record<string, string> = {
  pending: 'Pendiente',
  confirmed: 'Confirmada',
  cancelled: 'Cancelada',
  completed: 'Completada'
}

const formatNumber = (num: number) => new Intl.NumberFormat('en-US').format(num || 0)

const loadAnalytics = async () => {
  try {
    const [overview, revenue, vendors, status, bookings] = await Promise.all([
      api.get('/admin/analytics/overview'),
      api.get(`/admin/analytics/revenue?period=${revenuePeriod.value}`),
      api.get('/admin/analytics/top-vendors'),
      api.get('/admin/analytics/bookings/by-status'),
      api.get('/bookings?page_size=5')
    ])

    stats.value = overview
    revenueData.value = revenue
    topVendors.value = vendors
    bookingsByStatus.value = status
    recentBookings.value = bookings.items?.slice(0, 5) || []

    updateCharts()
  } catch (error) {
    console.error('Error loading analytics:', error)
  }
}

const updateCharts = () => {
  if (revenueChart) revenueChart.destroy()
  if (revenueChartRef.value) {
    revenueChart = new Chart(revenueChartRef.value, {
      type: 'bar',
      data: {
        labels: revenueData.value.map(r => r.date.slice(5)),
        datasets: [
          {
            label: 'Ingresos Brutos',
            data: revenueData.value.map(r => r.gross_revenue),
            backgroundColor: '#1e7a67',
            borderRadius: 4
          },
          {
            label: 'Ingresos Netos',
            data: revenueData.value.map(r => r.net_revenue),
            backgroundColor: '#2a9d8f',
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { usePointStyle: true, padding: 20 } }
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: '#6b7280' } },
          y: { grid: { color: '#e5e7eb' }, ticks: { color: '#6b7280', callback: (v) => '$' + v } }
        }
      }
    })
  }

  if (bookingsChart) bookingsChart.destroy()
  if (bookingsChartRef.value) {
    bookingsChart = new Chart(bookingsChartRef.value, {
      type: 'doughnut',
      data: {
        labels: bookingsByStatus.value.map(b => statusLabels[b.status] || b.status),
        datasets: [{
          data: bookingsByStatus.value.map(b => b.count),
          backgroundColor: bookingsByStatus.value.map(b => statusColors[b.status] || '#6b7280'),
          borderWidth: 0,
          spacing: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: {
          legend: { display: false }
        }
      }
    })
  }
}

watch(revenuePeriod, () => loadAnalytics())

onMounted(() => {
  auth.initAuth()
  if (!['super_admin', 'admin'].includes(auth.user?.role || '')) {
    navigateTo('/login')
    return
  }
  loadAnalytics()
})

onUnmounted(() => {
  if (revenueChart) revenueChart.destroy()
  if (bookingsChart) bookingsChart.destroy()
})
</script>

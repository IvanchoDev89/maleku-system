<script setup lang="ts">
/**
 * Analytics Dashboard
 * Dashboard de analíticas con datos reales de la base de datos
 */
import { ref, onMounted } from 'vue'
import { TrendingUp, Users, MousePointer, Clock, UserPlus, BarChart3, Mail, Eye, ShoppingCart, FileText, MapPin, Star } from 'lucide-vue-next'

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()
const loading = ref(false)

const activeTab = ref<'overview' | 'marketing' | 'content'>('overview')

const overviewStats = ref({
  totalUsers: 0,
  totalVendors: 0,
  totalBookings: 0,
  totalRevenue: 0,
  netRevenue: 0,
  newUsersToday: 0,
  activeUsersToday: 0,
  bookingsToday: 0,
  bookingsThisMonth: 0,
  revenueToday: 0,
  revenueThisMonth: 0,
  pendingVendors: 0,
  averageRating: 0,
  totalProperties: 0,
  totalTours: 0,
  totalReviews: 0,
  newsletterSubscribers: 0,
})

const marketingStats = ref({
  total_campaigns: 0,
  total_emails_sent: 0,
  total_opens: 0,
  total_clicks: 0,
  avg_open_rate: 0,
  avg_click_rate: 0,
})

const contentStats = ref({
  totalBlogPosts: 0,
  publishedPosts: 0,
  totalDestinations: 0,
})

const loadAnalytics = async () => {
  loading.value = true
  try {
    const [dashboardData, marketingData] = await Promise.allSettled([
      api.get('/superadmin/dashboard/stats'),
      api.get('/marketing/admin/analytics/overview').catch(() => null),
    ])

    if (dashboardData.status === 'fulfilled') {
      const d = dashboardData.value
      overviewStats.value = {
        totalUsers: d.total_users || 0,
        totalVendors: d.total_vendors || 0,
        totalBookings: d.total_bookings || 0,
        totalRevenue: d.total_revenue || 0,
        netRevenue: d.net_revenue || 0,
        newUsersToday: d.new_users_today || 0,
        activeUsersToday: d.active_users_today || 0,
        bookingsToday: d.bookings_today || 0,
        bookingsThisMonth: d.bookings_this_month || 0,
        revenueToday: d.revenue_today || 0,
        revenueThisMonth: d.revenue_this_month || 0,
        pendingVendors: d.pending_vendors || 0,
        averageRating: d.average_rating || 0,
        totalProperties: d.total_properties || 0,
        totalTours: d.total_tours || 0,
        totalReviews: d.total_reviews || 0,
        newsletterSubscribers: d.newsletter_subscribers || 0,
      }
    }

    if (marketingData.status === 'fulfilled' && marketingData.value) {
      marketingStats.value = marketingData.value
    }
  } catch {
    // stats stay at defaults
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAnalytics()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Analytics</h1>
        <p class="mt-1 text-gray-500">Métricas del sistema en tiempo real</p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <UiSpinner size="md" color="primary" />
    </div>

    <template v-else>
      <!-- Tabs -->
      <div class="border-b border-gray-200">
        <nav class="-mb-px flex space-x-8">
          <button
            v-for="tab in ['overview', 'marketing', 'content']"
            :key="tab"
            @click="activeTab = tab as any"
            :class="[
              activeTab === tab
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm capitalize'
            ]"
          >
            {{ tab === 'overview' ? 'Resumen' : tab === 'marketing' ? 'Marketing' : 'Contenido' }}
          </button>
        </nav>
      </div>

      <!-- Overview Tab -->
      <div v-if="activeTab === 'overview'">
        <!-- Top Row: Core metrics -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div class="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500">Usuarios Totales</p>
                <p class="text-3xl font-bold text-gray-900">{{ overviewStats.totalUsers.toLocaleString() }}</p>
              </div>
              <Users class="w-8 h-8 text-blue-500" />
            </div>
            <p class="text-sm text-green-600 mt-2">+{{ overviewStats.newUsersToday }} hoy</p>
          </div>

          <div class="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500">Reservas</p>
                <p class="text-3xl font-bold text-gray-900">{{ overviewStats.totalBookings.toLocaleString() }}</p>
              </div>
              <ShoppingCart class="w-8 h-8 text-green-500" />
            </div>
            <p class="text-sm text-green-600 mt-2">{{ overviewStats.bookingsToday }} hoy • {{ overviewStats.bookingsThisMonth }} este mes</p>
          </div>

          <div class="bg-white rounded-lg shadow p-6 border-l-4 border-emerald-500">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500">Ingresos</p>
                <p class="text-3xl font-bold text-gray-900">${{ overviewStats.totalRevenue.toLocaleString() }}</p>
              </div>
              <BarChart3 class="w-8 h-8 text-emerald-500" />
            </div>
            <p class="text-sm text-green-600 mt-2">${{ overviewStats.revenueToday.toLocaleString() }} hoy</p>
          </div>

          <div class="bg-white rounded-lg shadow p-6 border-l-4 border-purple-500">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm text-gray-500">Proveedores</p>
                <p class="text-3xl font-bold text-gray-900">{{ overviewStats.totalVendors.toLocaleString() }}</p>
              </div>
              <TrendingUp class="w-8 h-8 text-purple-500" />
            </div>
            <p class="text-sm text-yellow-600 mt-2">{{ overviewStats.pendingVendors }} pendientes</p>
          </div>
        </div>

        <!-- Secondary Row: More metrics -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="bg-white rounded-lg shadow p-5">
            <p class="text-sm text-gray-500">Ingreso Neto</p>
            <p class="text-2xl font-bold text-gray-900">${{ overviewStats.netRevenue.toLocaleString() }}</p>
            <p class="text-xs text-gray-400 mt-1">Después de comisiones</p>
          </div>
          <div class="bg-white rounded-lg shadow p-5">
            <p class="text-sm text-gray-500">Usuarios Activos Hoy</p>
            <p class="text-2xl font-bold text-blue-600">{{ overviewStats.activeUsersToday.toLocaleString() }}</p>
          </div>
          <div class="bg-white rounded-lg shadow p-5">
            <p class="text-sm text-gray-500">Rating Promedio</p>
            <p class="text-2xl font-bold text-yellow-500">{{ overviewStats.averageRating.toFixed(1) }} / 5</p>
            <p class="text-xs text-gray-400 mt-1">{{ overviewStats.totalReviews }} reseñas</p>
          </div>
        </div>
      </div>

      <!-- Marketing Tab -->
      <div v-if="activeTab === 'marketing'">
        <div v-if="marketingStats.total_campaigns === 0" class="bg-white rounded-lg shadow p-8 text-center">
          <Mail class="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p class="text-gray-500">No hay datos de marketing disponibles</p>
          <p class="text-sm text-gray-400 mt-1">Configura campañas de email marketing para ver estadísticas aquí</p>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="bg-white rounded-lg shadow p-6">
            <p class="text-sm text-gray-500">Campañas</p>
            <p class="text-3xl font-bold text-gray-900">{{ marketingStats.total_campaigns }}</p>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <p class="text-sm text-gray-500">Emails Enviados</p>
            <p class="text-3xl font-bold text-gray-900">{{ marketingStats.total_emails_sent.toLocaleString() }}</p>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <p class="text-sm text-gray-500">Tasa de Apertura</p>
            <p class="text-3xl font-bold text-green-600">{{ (marketingStats.avg_open_rate * 100).toFixed(1) }}%</p>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <p class="text-sm text-gray-500">Clicks</p>
            <p class="text-3xl font-bold text-gray-900">{{ marketingStats.total_clicks.toLocaleString() }}</p>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <p class="text-sm text-gray-500">Tasa de Click</p>
            <p class="text-3xl font-bold text-blue-600">{{ (marketingStats.avg_click_rate * 100).toFixed(1) }}%</p>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <p class="text-sm text-gray-500">Suscriptores Newsletter</p>
            <p class="text-3xl font-bold text-gray-900">{{ overviewStats.newsletterSubscribers.toLocaleString() }}</p>
          </div>
        </div>
      </div>

      <!-- Content Tab -->
      <div v-if="activeTab === 'content'">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center gap-3">
              <FileText class="w-8 h-8 text-blue-500" />
              <div>
                <p class="text-sm text-gray-500">Artículos Blog</p>
                <p class="text-2xl font-bold">{{ overviewStats.totalBlogPosts || '—' }}</p>
              </div>
            </div>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center gap-3">
              <Eye class="w-8 h-8 text-green-500" />
              <div>
                <p class="text-sm text-gray-500">Publicados</p>
                <p class="text-2xl font-bold text-green-600">{{ overviewStats.publishedPosts || '—' }}</p>
              </div>
            </div>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center gap-3">
              <MapPin class="w-8 h-8 text-purple-500" />
              <div>
                <p class="text-sm text-gray-500">Destinos</p>
                <p class="text-2xl font-bold">{{ overviewStats.totalDestinations || '—' }}</p>
              </div>
            </div>
          </div>
          <div class="bg-white rounded-lg shadow p-6">
            <div class="flex items-center gap-3">
              <Star class="w-8 h-8 text-yellow-500" />
              <div>
                <p class="text-sm text-gray-500">Rating Prom.</p>
                <p class="text-2xl font-bold text-yellow-500">{{ overviewStats.averageRating.toFixed(1) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

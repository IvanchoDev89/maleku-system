<template>
  <div>
    <!-- Header -->
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-2xl font-bold">{{ $t('vendor.dashboard') }}</h1>
        <p class="text-gray-500">Bienvenido, {{ user?.full_name }}</p>
      </div>
      <div class="flex items-center gap-4">
        <button class="p-2 bg-white rounded-lg shadow hover:bg-gray-50">
          🔔
        </button>
        <div class="w-10 h-10 bg-primary rounded-full flex items-center justify-center text-white font-bold">
          {{ user?.full_name?.charAt(0) || 'U' }}
        </div>
      </div>
    </div>

    <div v-if="loadingStats" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div v-for="i in 4" :key="i" class="bg-white rounded-xl shadow-sm p-6 animate-pulse">
        <div class="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
        <div class="h-8 bg-gray-200 rounded w-3/4"></div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-xl shadow-sm p-6 border-l-4 border-primary">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500 text-sm">Total Reservas</p>
            <p class="text-3xl font-bold">{{ stats.total_bookings }}</p>
          </div>
          <span class="text-3xl">📋</span>
        </div>
        <p class="text-sm text-green-600 mt-2">Tus reservas totales</p>
      </div>

      <div class="bg-white rounded-xl shadow-sm p-6 border-l-4 border-green-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500 text-sm">Ingresos Totales</p>
            <p class="text-3xl font-bold">${{ stats.total_revenue?.toLocaleString() || 0 }}</p>
          </div>
          <span class="text-3xl">💰</span>
        </div>
        <p class="text-sm text-green-600 mt-2">Ganancias acumuladas</p>
      </div>

      <div class="bg-white rounded-xl shadow-sm p-6 border-l-4 border-yellow-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500 text-sm">Pendientes</p>
            <p class="text-3xl font-bold">{{ stats.pending_bookings }}</p>
          </div>
          <span class="text-3xl">⏳</span>
        </div>
        <p class="text-sm text-gray-500 mt-2">Esperando confirmación</p>
      </div>

      <div class="bg-white rounded-xl shadow-sm p-6 border-l-4 border-purple-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500 text-sm">Propiedades</p>
            <p class="text-3xl font-bold">{{ stats.total_properties || 0 }}</p>
          </div>
          <span class="text-3xl">🏨</span>
        </div>
        <p class="text-sm text-green-600 mt-2">Propiedades activas</p>
      </div>
    </div>

    <!-- Recent Bookings -->
    <div class="bg-white rounded-xl shadow-sm p-6 mb-8">
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-bold text-lg">Reservas Recientes</h3>
        <NuxtLink to="/vendor/bookings" class="text-primary hover:underline">
          Ver todas →
        </NuxtLink>
      </div>
      
      <div v-if="loadingBookings" class="text-center py-4">
        <p class="text-gray-500">Cargando...</p>
      </div>
      
      <div v-else-if="recentBookings.length === 0" class="text-center py-8 text-gray-500">
        No tienes reservas aún.
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b">
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Código</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Cliente</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Servicio</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Fecha</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Monto</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="booking in recentBookings" 
              :key="booking.id"
              class="border-b hover:bg-gray-50"
            >
              <td class="py-3 px-4 font-mono text-sm">{{ booking.confirmation_code || booking.id?.slice(0, 8).toUpperCase() }}</td>
              <td class="py-3 px-4">{{ booking.guest_name }}</td>
              <td class="py-3 px-4">{{ booking.property_name || booking.tour_name || 'N/A' }}</td>
              <td class="py-3 px-4 text-sm">{{ formatDate(booking.created_at) }}</td>
              <td class="py-3 px-4 font-semibold">${{ booking.total_amount }}</td>
              <td class="py-3 px-4">
                <UiBadge :variant="statusBadgeVariant(booking.status)">
                  {{ getStatusLabel(booking.status) }}
                </UiBadge>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <NuxtLink 
        to="/vendor/properties/new"
        class="bg-gradient-to-r from-primary to-primary-light text-white rounded-xl p-6 hover:shadow-lg transition-shadow"
      >
        <div class="text-3xl mb-3">🏨</div>
        <h3 class="font-bold text-lg mb-1">{{ $t('vendor.addProperty') }}</h3>
        <p class="text-white/80 text-sm">Agrega un nuevo hotel o villa</p>
      </NuxtLink>

      <NuxtLink 
        to="/vendor/tours/new"
        class="bg-gradient-to-r from-accent to-accent-light text-white rounded-xl p-6 hover:shadow-lg transition-shadow"
      >
        <div class="text-3xl mb-3">🧗</div>
        <h3 class="font-bold text-lg mb-1">{{ $t('vendor.addTour') }}</h3>
        <p class="text-white/80 text-sm">Crea un nuevo tour</p>
      </NuxtLink>

      <NuxtLink 
        to="/vendor/settings"
        class="bg-gradient-to-r from-secondary to-dark text-white rounded-xl p-6 hover:shadow-lg transition-shadow"
      >
        <div class="text-3xl mb-3">⚙️</div>
        <h3 class="font-bold text-lg mb-1">{{ $t('vendor.settings') }}</h3>
        <p class="text-white/80 text-sm">Configura tu perfil</p>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'vendor',
  middleware: ['auth']
})

const auth = useAuthStore()
const api = useApi()

const user = computed(() => auth.user)

const stats = ref<any>({
  total_bookings: 0,
  total_revenue: 0,
  pending_bookings: 0,
  total_properties: 0
})
const loadingStats = ref(true)

const recentBookings = ref<any[]>([])
const loadingBookings = ref(true)

const fetchStats = async () => {
  loadingStats.value = true
  try {
    const data = await api.get<any>('/vendors/me/analytics')
    stats.value = data
  } catch (e) {
    console.error('Error loading stats:', e)
  } finally {
    loadingStats.value = false
  }
}

const fetchRecentBookings = async () => {
  loadingBookings.value = true
  try {
    const data = await api.get<any[]>('/bookings/vendor/my-bookings')
    recentBookings.value = data.slice(0, 5)
  } catch (e) {
    console.error('Error loading bookings:', e)
  } finally {
    loadingBookings.value = false
  }
}

const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('es-CR')
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    pending: 'Pendiente',
    confirmed: 'Confirmado',
    cancelled: 'Cancelado',
    completed: 'Completado'
  }
  return labels[status] || status
}

function statusBadgeVariant(status: string) {
  const map: Record<string, string> = {
    pending: 'warning',
    confirmed: 'success',
    cancelled: 'danger',
    completed: 'info'
  }
  return (map[status] || 'default') as any
}

onMounted(() => {
  fetchStats()
  fetchRecentBookings()
})
</script>
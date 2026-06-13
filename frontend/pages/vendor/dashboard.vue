<template>
  <div>
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
      <div>
        <h1 class="text-2xl font-bold">{{ $t('vendor.dashboard') }}</h1>
        <p class="text-gray-500">Bienvenido de vuelta, {{ user?.full_name }}</p>
      </div>
      <div class="flex items-center gap-3">
        <NuxtLink to="/vendor/properties/new" class="inline-flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium">
          <Icon name="lucide:plus" class="w-4 h-4" />
          Nueva Propiedad
        </NuxtLink>
      </div>
    </div>

    <div v-if="loadingStats" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div v-for="i in 4" :key="i" class="bg-white rounded-xl shadow-sm p-6 animate-pulse">
        <div class="h-4 bg-gray-200 rounded w-1/2 mb-3"></div>
        <div class="h-8 bg-gray-200 rounded w-3/4"></div>
      </div>
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div class="bg-white rounded-xl shadow-sm p-6 border-l-4 border-primary-500 hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500 text-sm font-medium">Total Reservas</p>
            <p class="text-3xl font-bold text-gray-900 mt-1">{{ stats.total_bookings }}</p>
          </div>
          <div class="w-12 h-12 bg-primary-50 rounded-xl flex items-center justify-center">
            <Icon name="lucide:calendar-check" class="w-6 h-6 text-primary-600" />
          </div>
        </div>
        <p class="text-sm text-gray-500 mt-3">Tus reservas totales</p>
      </div>

      <div class="bg-white rounded-xl shadow-sm p-6 border-l-4 border-green-500 hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500 text-sm font-medium">Ingresos Totales</p>
            <p class="text-3xl font-bold text-gray-900 mt-1">${{ stats.total_revenue?.toLocaleString() || 0 }}</p>
          </div>
          <div class="w-12 h-12 bg-green-50 rounded-xl flex items-center justify-center">
            <Icon name="lucide:dollar-sign" class="w-6 h-6 text-green-600" />
          </div>
        </div>
        <p class="text-sm text-gray-500 mt-3">Ganancias acumuladas</p>
      </div>

      <div class="bg-white rounded-xl shadow-sm p-6 border-l-4 border-amber-500 hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500 text-sm font-medium">Pendientes</p>
            <p class="text-3xl font-bold text-gray-900 mt-1">{{ stats.pending_bookings }}</p>
          </div>
          <div class="w-12 h-12 bg-amber-50 rounded-xl flex items-center justify-center">
            <Icon name="lucide:clock" class="w-6 h-6 text-amber-600" />
          </div>
        </div>
        <p class="text-sm text-gray-500 mt-3">Esperando confirmación</p>
      </div>

      <div class="bg-white rounded-xl shadow-sm p-6 border-l-4 border-purple-500 hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500 text-sm font-medium">Propiedades</p>
            <p class="text-3xl font-bold text-gray-900 mt-1">{{ stats.total_properties || 0 }}</p>
          </div>
          <div class="w-12 h-12 bg-purple-50 rounded-xl flex items-center justify-center">
            <Icon name="lucide:building-2" class="w-6 h-6 text-purple-600" />
          </div>
        </div>
        <p class="text-sm text-gray-500 mt-3">Propiedades activas</p>
      </div>
    </div>

    <div class="bg-white rounded-xl shadow-sm p-6 mb-8">
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-bold text-lg">Reservas Recientes</h3>
        <NuxtLink to="/vendor/bookings" class="text-primary-600 hover:text-primary-700 text-sm font-medium hover:underline">
          Ver todas →
        </NuxtLink>
      </div>

      <div v-if="loadingBookings" class="space-y-3">
        <div v-for="i in 3" :key="i" class="flex gap-4 animate-pulse">
          <div class="h-4 bg-gray-200 rounded w-20" />
          <div class="h-4 bg-gray-200 rounded w-32" />
          <div class="h-4 bg-gray-200 rounded flex-1" />
          <div class="h-4 bg-gray-200 rounded w-20" />
        </div>
      </div>

      <div v-else-if="recentBookings.length === 0" class="text-center py-12">
        <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Icon name="lucide:calendar-x" class="w-8 h-8 text-gray-400" />
        </div>
        <p class="text-gray-500 font-medium">No tienes reservas aún</p>
        <p class="text-gray-400 text-sm mt-1">Cuando recibas reservas aparecerán aquí</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-100">
              <th class="text-left py-3 px-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Código</th>
              <th class="text-left py-3 px-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Cliente</th>
              <th class="text-left py-3 px-3 font-semibold text-gray-500 text-xs uppercase tracking-wider hidden sm:table-cell">Servicio</th>
              <th class="text-left py-3 px-3 font-semibold text-gray-500 text-xs uppercase tracking-wider hidden md:table-cell">Fecha</th>
              <th class="text-left py-3 px-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Monto</th>
              <th class="text-left py-3 px-3 font-semibold text-gray-500 text-xs uppercase tracking-wider">Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="booking in recentBookings"
              :key="booking.id"
              class="border-b border-gray-50 hover:bg-gray-50 transition-colors"
            >
              <td class="py-3 px-3 font-mono text-sm text-gray-900">{{ booking.confirmation_code || booking.id?.slice(0, 8).toUpperCase() }}</td>
              <td class="py-3 px-3 text-gray-900">{{ booking.guest_name }}</td>
              <td class="py-3 px-3 text-gray-600 hidden sm:table-cell">{{ booking.property_name || booking.tour_name || 'N/A' }}</td>
              <td class="py-3 px-3 text-sm text-gray-500 hidden md:table-cell">{{ formatDate(booking.created_at) }}</td>
              <td class="py-3 px-3 font-semibold text-gray-900">${{ booking.total_amount }}</td>
              <td class="py-3 px-3">
                <UiBadge :variant="statusBadgeVariant(booking.status)">
                  {{ getStatusLabel(booking.status) }}
                </UiBadge>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <NuxtLink
        to="/vendor/properties/new"
        class="group bg-gradient-to-br from-primary-600 to-primary-700 text-white rounded-xl p-6 hover:shadow-lg transition-all duration-200 hover:-translate-y-0.5"
      >
        <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
          <Icon name="lucide:building-2" class="w-6 h-6" />
        </div>
        <h3 class="font-bold text-lg mb-1">{{ $t('vendor.addProperty') }}</h3>
        <p class="text-white/80 text-sm">Agrega un nuevo hotel o villa</p>
      </NuxtLink>

      <NuxtLink
        to="/vendor/tours/new"
        class="group bg-gradient-to-br from-accent-600 to-accent-700 text-white rounded-xl p-6 hover:shadow-lg transition-all duration-200 hover:-translate-y-0.5"
      >
        <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
          <Icon name="lucide:mountain" class="w-6 h-6" />
        </div>
        <h3 class="font-bold text-lg mb-1">{{ $t('vendor.addTour') }}</h3>
        <p class="text-white/80 text-sm">Crea un nuevo tour o experiencia</p>
      </NuxtLink>

      <NuxtLink
        to="/vendor/settings"
        class="group bg-gradient-to-br from-slate-700 to-slate-800 text-white rounded-xl p-6 hover:shadow-lg transition-all duration-200 hover:-translate-y-0.5"
      >
        <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
          <Icon name="lucide:settings" class="w-6 h-6" />
        </div>
        <h3 class="font-bold text-lg mb-1">{{ $t('vendor.settings') }}</h3>
        <p class="text-white/80 text-sm">Configura tu perfil y pagos</p>
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
    const data = await api.get<{ items: any[]; total: number }>('/bookings/vendor/my-bookings')
    recentBookings.value = (data.items || []).slice(0, 5)
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

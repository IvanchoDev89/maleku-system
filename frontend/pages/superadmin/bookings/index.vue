<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()

interface Booking {
  id: string
  guest_name: string
  guest_email: string
  booking_type: string
  status: string
  total_amount: number
  created_at: string
  vendor_id?: string
  property_id?: string
  tour_id?: string
}

const bookings = ref<Booking[]>([])
const loading = ref(true)
const currentPage = ref(1)
const totalPages = ref(1)
const totalItems = ref(0)
const pageSize = ref(20)

const filterStatus = ref<string>('all')
const searchQuery = ref('')

const statusOptions = [
  { value: 'all', label: 'Todos' },
  { value: 'pending', label: 'Pendiente' },
  { value: 'confirmed', label: 'Confirmada' },
  { value: 'completed', label: 'Completada' },
  { value: 'cancelled', label: 'Cancelada' },
]

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  confirmed: 'bg-green-100 text-green-800',
  completed: 'bg-blue-100 text-blue-800',
  cancelled: 'bg-red-100 text-red-800',
  refunded: 'bg-gray-100 text-gray-800'
}

const statusLabels: Record<string, string> = {
  pending: 'Pendiente',
  confirmed: 'Confirmada',
  completed: 'Completada',
  cancelled: 'Cancelada',
  refunded: 'Reembolsada'
}

const fetchBookings = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (filterStatus.value !== 'all') params.status = filterStatus.value

    const response = await api.get('/superadmin/bookings', params)
    bookings.value = response.items || []
    totalPages.value = response.total_pages || 1
    totalItems.value = response.total || 0
  } catch (error) {
    console.error('Error fetching bookings:', error)
    bookings.value = []
  } finally {
    loading.value = false
  }
}

const filteredBookings = computed(() => {
  if (!searchQuery.value) return bookings.value
  const q = searchQuery.value.toLowerCase()
  return bookings.value.filter(b =>
    b.guest_name?.toLowerCase().includes(q) ||
    b.id?.toLowerCase().includes(q) ||
    b.guest_email?.toLowerCase().includes(q)
  )
})

const totalRevenue = computed(() =>
  bookings.value
    .filter(b => b.status === 'confirmed' || b.status === 'completed')
    .reduce((sum, b) => sum + (b.total_amount || 0), 0)
)

const confirmedCount = computed(() => bookings.value.filter(b => b.status === 'confirmed').length)
const pendingCount = computed(() => bookings.value.filter(b => b.status === 'pending').length)

const changePage = (page: number) => {
  currentPage.value = page
  fetchBookings()
}

onMounted(() => {
  fetchBookings()
})

watch(filterStatus, () => {
  currentPage.value = 1
  fetchBookings()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Reservas</h1>
        <p class="mt-1 text-gray-500">Gestion de todas las reservas del sistema</p>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Total Reservas</div>
        <div class="text-3xl font-bold text-gray-900">{{ totalItems }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Confirmadas</div>
        <div class="text-3xl font-bold text-green-600">{{ confirmedCount }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Pendientes</div>
        <div class="text-3xl font-bold text-yellow-600">{{ pendingCount }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Ingresos</div>
        <div class="text-3xl font-bold text-blue-600">${{ totalRevenue.toLocaleString() }}</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex flex-wrap gap-4">
        <div class="flex-1 min-w-[200px]">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar por nombre, email o ID..."
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <UiSelect v-model="filterStatus" :options="statusOptions" placeholder="Todos los estados" />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="bg-white rounded-lg shadow p-12 text-center">
      <UiSpinner size="lg" color="primary" class="mx-auto mb-4" />
      <p class="text-gray-500">Cargando reservas...</p>
    </div>

    <!-- Empty -->
    <div v-else-if="filteredBookings.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <p class="text-gray-400 text-lg">No se encontraron reservas</p>
    </div>

    <!-- Table -->
    <div v-else class="bg-white rounded-lg shadow overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cliente</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Tipo</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Monto</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Fecha</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="booking in filteredBookings" :key="booking.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                {{ booking.id?.slice(0, 8) }}...
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ booking.guest_name }}</div>
                <div class="text-sm text-gray-500">{{ booking.guest_email }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 hidden sm:table-cell">
                {{ booking.booking_type === 'property' ? 'Propiedad' : 'Tour' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                ${{ (booking.total_amount || 0).toLocaleString() }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 hidden md:table-cell">
                {{ new Date(booking.created_at).toLocaleDateString() }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="['px-2 py-1 text-xs font-medium rounded-full', statusColors[booking.status] || 'bg-gray-100 text-gray-800']">
                  {{ statusLabels[booking.status] || booking.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <p class="text-sm text-gray-700">
            Pagina <span class="font-medium">{{ currentPage }}</span> de <span class="font-medium">{{ totalPages }}</span>
          </p>
          <div class="flex space-x-2">
            <button
              @click="changePage(currentPage - 1)"
              :disabled="currentPage <= 1"
              class="px-3 py-1 border rounded text-sm disabled:opacity-50"
            >Anterior</button>
            <button
              @click="changePage(currentPage + 1)"
              :disabled="currentPage >= totalPages"
              class="px-3 py-1 border rounded text-sm disabled:opacity-50"
            >Siguiente</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

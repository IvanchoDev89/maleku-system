<script setup lang="ts">
definePageMeta({
  layout: 'vendor',
  middleware: ['auth']
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
}

const bookings = ref<Booking[]>([])
const loading = ref(true)
const currentPage = ref(1)
const totalPages = ref(1)
const totalItems = ref(0)

const fetchBookings = async () => {
  loading.value = true
  try {
    const response = await api.get('/bookings/vendor/my-bookings', {
      page: currentPage.value,
      page_size: 20,
    })
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

const completedBookings = computed(() =>
  bookings.value.filter(b => b.status === 'confirmed' || b.status === 'completed')
)

const totalEarnings = computed(() =>
  completedBookings.value.reduce((sum, b) => sum + (b.total_amount || 0), 0)
)

const pendingBookings = computed(() =>
  bookings.value.filter(b => b.status === 'pending')
)

const pendingAmount = computed(() =>
  pendingBookings.value.reduce((sum, b) => sum + (b.total_amount || 0), 0)
)

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  confirmed: 'bg-green-100 text-green-800',
  completed: 'bg-blue-100 text-blue-800',
  cancelled: 'bg-red-100 text-red-800',
}

const statusLabels: Record<string, string> = {
  pending: 'Pendiente',
  confirmed: 'Confirmada',
  completed: 'Completada',
  cancelled: 'Cancelada',
}

onMounted(() => {
  fetchBookings()
})
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-2xl font-bold">Pagos</h1>
        <p class="text-gray-500">Historial de pagos y ganancias</p>
      </div>
    </div>

    <div class="space-y-6">
      <!-- Balance Card -->
      <div class="bg-white rounded-xl shadow-sm p-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p class="text-gray-500 text-sm">Ganancias Totales</p>
            <p class="text-3xl font-bold text-green-600">${{ totalEarnings.toLocaleString() }}</p>
          </div>
          <div>
            <p class="text-gray-500 text-sm">Pendiente</p>
            <p class="text-3xl font-bold text-yellow-600">${{ pendingAmount.toLocaleString() }}</p>
          </div>
          <div>
            <p class="text-gray-500 text-sm">Total Reservas</p>
            <p class="text-3xl font-bold">{{ totalItems }}</p>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="bg-white rounded-xl shadow-sm p-12 text-center">
        <UiSpinner size="lg" color="primary" class="mx-auto mb-4" />
        <p class="text-gray-500">Cargando historial...</p>
      </div>

      <!-- Payout History -->
      <div v-else class="bg-white rounded-xl shadow-sm overflow-hidden">
        <div class="p-4 border-b">
          <h3 class="font-bold">Historial de Reservas</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="text-left py-3 px-4 font-semibold text-gray-600 text-sm">ID</th>
                <th class="text-left py-3 px-4 font-semibold text-gray-600 text-sm">Cliente</th>
                <th class="text-left py-3 px-4 font-semibold text-gray-600 text-sm">Monto</th>
                <th class="text-left py-3 px-4 font-semibold text-gray-600 text-sm hidden sm:table-cell">Fecha</th>
                <th class="text-left py-3 px-4 font-semibold text-gray-600 text-sm">Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="booking in bookings" :key="booking.id" class="border-t hover:bg-gray-50">
                <td class="py-3 px-4 text-sm text-blue-600">{{ booking.id?.slice(0, 8) }}...</td>
                <td class="py-3 px-4 text-sm">{{ booking.guest_name }}</td>
                <td class="py-3 px-4 font-semibold text-sm">${{ (booking.total_amount || 0).toLocaleString() }}</td>
                <td class="py-3 px-4 text-sm hidden sm:table-cell">{{ new Date(booking.created_at).toLocaleDateString() }}</td>
                <td class="py-3 px-4">
                  <span :class="['px-2 py-1 rounded-full text-xs font-medium', statusColors[booking.status] || 'bg-gray-100 text-gray-800']">
                    {{ statusLabels[booking.status] || booking.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="p-4 border-t flex items-center justify-between">
          <p class="text-sm text-gray-500">Pagina {{ currentPage }} de {{ totalPages }}</p>
          <div class="flex space-x-2">
            <button @click="currentPage--; fetchBookings()" :disabled="currentPage <= 1" class="px-3 py-1 border rounded text-sm disabled:opacity-50">Anterior</button>
            <button @click="currentPage++; fetchBookings()" :disabled="currentPage >= totalPages" class="px-3 py-1 border rounded text-sm disabled:opacity-50">Siguiente</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

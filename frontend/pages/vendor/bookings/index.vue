<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-2xl font-bold">Mis Reservas</h1>
        <p class="text-gray-500">Gestiona las reservas de tus propiedades y tours</p>
      </div>
      <div class="flex gap-2">
        <UiSelect v-model="filter" :options="filterOptions" placeholder="Todos los estados" @update:model-value="onFilterChange" />
      </div>
    </div>

    <div v-if="error" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
      {{ error }}
      <button @click="fetchBookings" class="ml-3 underline hover:no-underline">Reintentar</button>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-8 space-y-4">
        <div v-for="i in 5" :key="i" class="flex gap-4 animate-pulse">
          <div class="h-4 bg-gray-200 rounded w-20" />
          <div class="h-4 bg-gray-200 rounded w-32" />
          <div class="h-4 bg-gray-200 rounded w-24" />
          <div class="h-4 bg-gray-200 rounded w-32" />
          <div class="h-4 bg-gray-200 rounded w-20" />
          <div class="h-4 bg-gray-200 rounded w-16" />
          <div class="h-4 bg-gray-200 rounded w-24" />
        </div>
      </div>
    </div>

    <div v-else class="bg-white rounded-xl shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Código</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600 hidden sm:table-cell">Servicio</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Cliente</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600 hidden md:table-cell">Fechas</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Estado</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600 hidden sm:table-cell">Monto</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="bookings.length === 0">
              <td colspan="7" class="text-center py-12 text-gray-500">
                No tienes reservas aún.
              </td>
            </tr>
            <tr
              v-for="booking in bookings"
              :key="booking.id"
              class="border-t hover:bg-gray-50"
            >
              <td class="py-3 px-4 font-mono text-sm">
                {{ booking.confirmation_code || booking.id.slice(0, 8).toUpperCase() }}
              </td>
              <td class="py-3 px-4 hidden sm:table-cell">
                <div class="font-medium">{{ booking.property_name || booking.tour_name || 'N/A' }}</div>
                <div class="text-xs text-gray-500">{{ booking.booking_type }}</div>
              </td>
              <td class="py-3 px-4">
                <div>{{ booking.guest_name }}</div>
                <div class="text-sm text-gray-500">{{ booking.guest_email }}</div>
              </td>
              <td class="py-3 px-4 text-sm hidden md:table-cell">
                <div v-if="booking.check_in && booking.check_out">
                  {{ formatDate(booking.check_in) }} - {{ formatDate(booking.check_out) }}
                </div>
                <div v-else-if="booking.created_at">
                  {{ formatDate(booking.created_at) }}
                </div>
              </td>
              <td class="py-3 px-4">
                <UiBadge :variant="statusBadgeVariant(booking.status)">
                  {{ getStatusLabel(booking.status) }}
                </UiBadge>
              </td>
              <td class="py-3 px-4 font-semibold hidden sm:table-cell">
                ${{ booking.total_amount }}
              </td>
              <td class="py-3 px-4">
                <div v-if="booking.status === 'pending'" class="flex gap-2">
                  <button @click="updateStatus(booking.id, 'confirmed')" class="text-green-600 hover:underline text-sm">
                    Confirmar
                  </button>
                  <button @click="openCancelDialog(booking)" class="text-red-600 hover:underline text-sm">
                    Cancelar
                  </button>
                </div>
                <div v-else-if="booking.status === 'confirmed'" class="flex gap-2">
                  <button @click="updateStatus(booking.id, 'completed')" class="text-blue-600 hover:underline text-sm">
                    Completar
                  </button>
                  <button @click="openCancelDialog(booking)" class="text-red-600 hover:underline text-sm">
                    Cancelar
                  </button>
                </div>
                <span v-else class="text-gray-400 text-sm">-</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="total > pageSize" class="flex items-center justify-between mt-4">
      <p class="text-sm text-gray-500">
        Mostrando {{ (page - 1) * pageSize + 1 }}-{{ Math.min(page * pageSize, total) }} de {{ total }}
      </p>
      <div class="flex gap-1">
        <button
          :disabled="page <= 1"
          class="px-3 py-1.5 text-sm rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          @click="changePage(page - 1)"
        >Anterior</button>
        <button
          v-for="p in totalPages"
          :key="p"
          :class="['px-3 py-1.5 text-sm rounded-lg transition-colors', p === page ? 'bg-primary-600 text-white' : 'border border-gray-200 hover:bg-gray-50']"
          @click="changePage(p)"
        >{{ p }}</button>
        <button
          :disabled="page >= totalPages"
          class="px-3 py-1.5 text-sm rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          @click="changePage(page + 1)"
        >Siguiente</button>
      </div>
    </div>

    <!-- Cancel Confirmation -->
    <UiConfirmDialog
      :model-value="!!bookingToCancel"
      title="Cancelar Reserva"
      :message="`¿Estás seguro de cancelar esta reserva?`"
      confirm-text="Cancelar Reserva"
      variant="danger"
      :loading="cancelling"
      @update:model-value="bookingToCancel = null"
      @confirm="confirmCancel"
    />
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'vendor',
  middleware: ['auth']
})

const api = useApi()

const bookings = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const filter = ref('')
const bookingToCancel = ref<any>(null)
const cancelling = ref(false)

const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

const filterOptions = [
  { value: '', label: 'Todos los estados' },
  { value: 'pending', label: 'Pendientes' },
  { value: 'confirmed', label: 'Confirmados' },
  { value: 'cancelled', label: 'Cancelados' },
  { value: 'completed', label: 'Completados' }
]

const fetchBookings = async () => {
  loading.value = true
  error.value = ''
  try {
    const params: Record<string, any> = {
      page: page.value,
      page_size: pageSize.value
    }
    if (filter.value) params.status = filter.value
    const data = await api.get<{ items: any[]; total: number }>('/bookings/vendor/my-bookings', params)
    bookings.value = data.items || []
    total.value = data.total || bookings.value.length
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar reservas'
  } finally {
    loading.value = false
  }
}

const onFilterChange = () => {
  page.value = 1
  fetchBookings()
}

const changePage = (p: number) => {
  page.value = p
  fetchBookings()
}

const updateStatus = async (id: string, status: string) => {
  try {
    await api.put(`/bookings/${id}/status`, { status })
    fetchBookings()
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al actualizar estado'
  }
}

const openCancelDialog = (booking: any) => {
  bookingToCancel.value = booking
}

const confirmCancel = async () => {
  if (!bookingToCancel.value) return
  cancelling.value = true
  try {
    await api.put(`/bookings/${bookingToCancel.value.id}/status`, { status: 'cancelled' })
    bookingToCancel.value = null
    fetchBookings()
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cancelar reserva'
  } finally {
    cancelling.value = false
  }
}

const formatDate = (date: string) => {
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
  fetchBookings()
})
</script>

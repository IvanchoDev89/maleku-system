<template>
  <div>
    <div v-if="error" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
      {{ error }}
      <button @click="fetchBookings" class="ml-3 underline hover:no-underline">Reintentar</button>
    </div>

    <div class="flex flex-wrap gap-4 mb-6">
      <div class="relative flex-1 min-w-[200px]">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar reserva..."
          class="w-full pl-11 pr-4 py-2.5 bg-white text-gray-700 rounded-xl border border-gray-200 shadow-sm focus:border-primary focus:ring-2 focus:ring-primary/20"
          @input="debouncedSearch"
        />
        <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
      <UiSelect v-model="statusFilter" :options="statusOptions" placeholder="Todos los estados" @update:model-value="fetchBookings" />
      <UiSelect v-model="typeFilter" :options="typeOptions" placeholder="Todos los tipos" @update:model-value="fetchBookings" />
      <button @click="exportCSV" class="bg-gray-100 text-gray-700 px-4 py-2.5 rounded-xl hover:bg-gray-200 font-medium transition-colors flex items-center gap-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Exportar CSV
      </button>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-8 space-y-4">
        <div v-for="i in 5" :key="i" class="flex gap-4 animate-pulse">
          <div class="h-4 bg-gray-200 rounded w-20" />
          <div class="h-4 bg-gray-200 rounded w-40" />
          <div class="h-4 bg-gray-200 rounded w-32" />
          <div class="h-4 bg-gray-200 rounded w-16" />
          <div class="h-4 bg-gray-200 rounded w-20" />
          <div class="h-4 bg-gray-200 rounded w-24" />
          <div class="h-4 bg-gray-200 rounded w-28" />
          <div class="h-4 bg-gray-200 rounded w-16" />
        </div>
      </div>
    </div>

    <div v-else class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="text-left p-4 text-gray-500 font-semibold text-sm">Código</th>
              <th class="text-left p-4 text-gray-500 font-semibold text-sm">Cliente</th>
              <th class="text-left p-4 text-gray-500 font-semibold text-sm">Proveedor</th>
              <th class="text-left p-4 text-gray-500 font-semibold text-sm">Tipo</th>
              <th class="text-left p-4 text-gray-500 font-semibold text-sm">Monto</th>
              <th class="text-left p-4 text-gray-500 font-semibold text-sm">Estado</th>
              <th class="text-left p-4 text-gray-500 font-semibold text-sm">Fecha</th>
              <th class="text-left p-4 text-gray-500 font-semibold text-sm">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="booking in bookings" :key="booking.id" class="border-t border-gray-100 hover:bg-gray-50/50 transition-colors">
              <td class="p-4">
                <span class="font-mono text-primary font-medium">{{ booking.booking_code }}</span>
              </td>
              <td class="p-4 text-gray-700 font-medium">{{ booking.user_name }}</td>
              <td class="p-4 text-gray-500">{{ booking.vendor_name }}</td>
              <td class="p-4">
                <UiBadge variant="info" size="sm">{{ booking.booking_type }}</UiBadge>
              </td>
              <td class="p-4 text-gray-900 font-semibold">${{ booking.total_amount }}</td>
              <td class="p-4">
                <UiBadge :variant="statusBadgeVariant(booking.status)" size="sm">
                  {{ getStatusLabel(booking.status) }}
                </UiBadge>
              </td>
              <td class="p-4 text-gray-500 text-sm">{{ formatDate(booking.created_at) }}</td>
              <td class="p-4">
                <div class="flex gap-2">
                  <button @click="viewBooking(booking)" class="p-2 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors" title="Ver detalle">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                  <button v-if="booking.status === 'pending'" @click="confirmBooking(booking)" class="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors" title="Confirmar">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                  </button>
                  <button v-if="booking.status === 'pending'" @click="openCancelDialog(booking)" class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors" title="Cancelar">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="bookings.length === 0 && !loading" class="p-8 text-center text-gray-400">
        No hay reservas
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

    <!-- Detail Modal -->
    <UiModal v-if="selectedBooking" :model-value="!!selectedBooking" title="Detalle de Reserva" max-width="max-w-2xl" @update:model-value="selectedBooking = null">
      <div class="grid grid-cols-2 gap-4">
        <div class="bg-gray-50 p-4 rounded-xl">
          <p class="text-gray-500 text-sm">Cliente</p>
          <p class="text-gray-900 font-medium">{{ selectedBooking.user_name }}</p>
          <p class="text-gray-400 text-sm">{{ selectedBooking.user_email }}</p>
        </div>
        <div class="bg-gray-50 p-4 rounded-xl">
          <p class="text-gray-500 text-sm">Proveedor</p>
          <p class="text-gray-900 font-medium">{{ selectedBooking.vendor_name }}</p>
        </div>
        <div class="bg-gray-50 p-4 rounded-xl">
          <p class="text-gray-500 text-sm">Tipo</p>
          <p class="text-gray-900 font-medium capitalize">{{ selectedBooking.booking_type }}</p>
        </div>
        <div class="bg-gray-50 p-4 rounded-xl">
          <p class="text-gray-500 text-sm">Monto</p>
          <p class="text-gray-900 font-bold text-xl">${{ selectedBooking.total_amount }}</p>
        </div>
        <div class="bg-gray-50 p-4 rounded-xl">
          <p class="text-gray-500 text-sm">Estado</p>
          <UiBadge :variant="statusBadgeVariant(selectedBooking.status)" size="md">
            {{ getStatusLabel(selectedBooking.status) }}
          </UiBadge>
        </div>
        <div class="bg-gray-50 p-4 rounded-xl">
          <p class="text-gray-500 text-sm">Comisión (10%)</p>
          <p class="text-purple-600 font-bold">${{ (selectedBooking.total_amount * 0.1).toFixed(2) }}</p>
        </div>
      </div>
      <template #footer>
        <button @click="selectedBooking = null" class="px-4 py-2.5 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors">Cerrar</button>
      </template>
    </UiModal>

    <!-- Cancel Confirmation -->
    <UiConfirmDialog
      :model-value="!!bookingToCancel"
      title="Cancelar Reserva"
      :message="`¿Estás seguro de cancelar la reserva ${bookingToCancel?.booking_code}?`"
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
  layout: 'admin',
  middleware: ['auth']
})

const api = useApi()
const auth = useAuthStore()

interface Booking {
  id: string
  booking_code: string
  user_name: string
  user_email: string
  vendor_name: string
  booking_type: string
  total_amount: number
  status: string
  created_at: string
}

const bookings = ref<Booking[]>([])
const loading = ref(false)
const error = ref('')
const searchQuery = ref('')
const statusFilter = ref('')
const typeFilter = ref('')
const selectedBooking = ref<Booking | null>(null)
const bookingToCancel = ref<Booking | null>(null)
const cancelling = ref(false)

const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

const statusOptions = [
  { value: '', label: 'Todos los estados' },
  { value: 'pending', label: 'Pendiente' },
  { value: 'confirmed', label: 'Confirmada' },
  { value: 'cancelled', label: 'Cancelada' },
  { value: 'completed', label: 'Completada' }
]

const typeOptions = [
  { value: '', label: 'Todos los tipos' },
  { value: 'property', label: 'Hotel' },
  { value: 'tour', label: 'Tour' }
]

function statusBadgeVariant(status: string) {
  const map: Record<string, string> = {
    pending: 'warning',
    confirmed: 'success',
    cancelled: 'danger',
    completed: 'info'
  }
  return (map[status] || 'default') as any
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    pending: 'Pendiente',
    confirmed: 'Confirmada',
    cancelled: 'Cancelada',
    completed: 'Completada'
  }
  return labels[status] || status
}

const formatDate = (date: string) => new Date(date).toLocaleDateString('es-CR')

const fetchBookings = async () => {
  loading.value = true
  error.value = ''
  try {
    const params: Record<string, any> = {
      page: page.value,
      page_size: pageSize.value
    }
    if (searchQuery.value) params.search = searchQuery.value
    if (statusFilter.value) params.status = statusFilter.value
    if (typeFilter.value) params.booking_type = typeFilter.value
    const data = await api.get('/bookings', params)
    bookings.value = data.items || []
    total.value = data.total || bookings.value.length
  } catch (e) {
    error.value = 'Error al cargar reservas'
  } finally {
    loading.value = false
  }
}

let searchTimeout: ReturnType<typeof setTimeout>
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(fetchBookings, 300)
}

const changePage = (p: number) => {
  page.value = p
  fetchBookings()
}

const viewBooking = (booking: Booking) => { selectedBooking.value = booking }

const confirmBooking = async (booking: Booking) => {
  try {
    await api.patch(`/bookings/${booking.id}`, { status: 'confirmed' })
    fetchBookings()
  } catch (e) { console.error(e) }
}

const openCancelDialog = (booking: Booking) => {
  bookingToCancel.value = booking
}

const confirmCancel = async () => {
  if (!bookingToCancel.value) return
  cancelling.value = true
  try {
    await api.patch(`/bookings/${bookingToCancel.value.id}`, { status: 'cancelled' })
    bookingToCancel.value = null
    fetchBookings()
  } catch (e) { console.error(e) }
  finally { cancelling.value = false }
}

const exportCSV = () => {
  const data: string[][] = [['Código', 'Cliente', 'Proveedor', 'Tipo', 'Monto', 'Estado', 'Fecha']]
  bookings.value.forEach((b: Booking) => {
    data.push([b.booking_code, b.user_name, b.vendor_name, b.booking_type, String(b.total_amount), b.status, b.created_at])
  })
  downloadCSV(data, `reservas-${new Date().toISOString().split('T')[0]}.csv`)
}

watch(() => page.value, fetchBookings)

onMounted(() => {
  auth.initAuth()
  fetchBookings()
})
</script>

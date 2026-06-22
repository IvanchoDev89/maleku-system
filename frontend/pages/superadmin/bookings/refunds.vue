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
}

const refunds = ref<Booking[]>([])
const loading = ref(true)
const currentPage = ref(1)
const totalPages = ref(1)
const totalItems = ref(0)

const fetchRefunds = async () => {
  loading.value = true
  try {
    const response = await api.get('/superadmin/bookings', {
      page: currentPage.value,
      page_size: 20,
      status: 'cancelled',
    })
    refunds.value = response.items || []
    totalPages.value = response.total_pages || 1
    totalItems.value = response.total || 0
  } catch (error) {
    console.error('Error fetching refunds:', error)
    refunds.value = []
  } finally {
    loading.value = false
  }
}

const showConfirm = ref(false)
const confirmTitle = ref('')
const confirmMessage = ref('')
const confirmLoading = ref(false)
let pendingRefundBooking: Booking | null = null

const confirmProcessRefund = (booking: Booking) => {
  pendingRefundBooking = booking
  confirmTitle.value = 'Procesar Reembolso'
  confirmMessage.value = `Procesar reembolso para reserva ${booking.id?.slice(0, 8)}?`
  showConfirm.value = true
}

const executeRefund = async () => {
  if (!pendingRefundBooking) return
  confirmLoading.value = true
  try {
    await api.post(`/stripe/bookings/${pendingRefundBooking.id}/refund`, { reason: 'Admin initiated refund' })
    await fetchRefunds()
  } catch (error) {
    console.error('Error processing refund:', error)
  } finally {
    confirmLoading.value = false
    showConfirm.value = false
    pendingRefundBooking = null
  }
}

const changePage = (page: number) => {
  currentPage.value = page
  fetchRefunds()
}

const totalRefundAmount = computed(() =>
  refunds.value.reduce((sum, b) => sum + (b.total_amount || 0), 0)
)

onMounted(() => {
  fetchRefunds()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Reembolsos</h1>
        <p class="mt-1 text-gray-500">Gestion de solicitudes de reembolso (reservas canceladas)</p>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Total Canceladas</div>
        <div class="text-3xl font-bold text-gray-900">{{ totalItems }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Monto Total</div>
        <div class="text-3xl font-bold text-red-600">${{ totalRefundAmount.toLocaleString() }}</div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="bg-white rounded-lg shadow p-12 text-center">
      <UiSpinner size="lg" color="primary" class="mx-auto mb-4" />
      <p class="text-gray-500">Cargando reembolsos...</p>
    </div>

    <div v-else-if="refunds.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <p class="text-gray-400 text-lg">No hay reservas canceladas pendientes</p>
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
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="booking in refunds" :key="booking.id" class="hover:bg-gray-50">
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
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-red-600">
                ${{ (booking.total_amount || 0).toLocaleString() }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 hidden md:table-cell">
                {{ new Date(booking.created_at).toLocaleDateString() }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  @click="confirmProcessRefund(booking)"
                  class="text-primary-600 hover:text-primary-900"
                >
                  Procesar Reembolso
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200">
        <p class="text-sm text-gray-700">
          Pagina <span class="font-medium">{{ currentPage }}</span> de <span class="font-medium">{{ totalPages }}</span>
        </p>
        <div class="flex space-x-2">
          <button @click="changePage(currentPage - 1)" :disabled="currentPage <= 1" class="px-3 py-1 border rounded text-sm disabled:opacity-50">Anterior</button>
          <button @click="changePage(currentPage + 1)" :disabled="currentPage >= totalPages" class="px-3 py-1 border rounded text-sm disabled:opacity-50">Siguiente</button>
        </div>
      </div>
    </div>

    <!-- Confirm Dialog -->
    <UiConfirmDialog
      v-model="showConfirm"
      :title="confirmTitle"
      :message="confirmMessage"
      confirm-text="Procesar Reembolso"
      variant="warning"
      :loading="confirmLoading"
      @confirm="executeRefund"
    />
  </div>
</template>

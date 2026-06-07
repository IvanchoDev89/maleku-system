<script setup lang="ts">
/**
 * Bookings Management
 * Gestión de todas las reservas del sistema
 */
import { ref, computed } from 'vue'

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

interface Booking {
  id: string
  customer: string
  email: string
  service: string
  vendor: string
  checkIn: string
  checkOut: string
  amount: number
  status: 'pending' | 'confirmed' | 'cancelled' | 'refunded'
  createdAt: string
}

const bookings = ref<Booking[]>([
  { id: 'BK-001', customer: 'John Smith', email: 'john@email.com', service: 'Hotel Costa Verde', vendor: 'Hoteles CR', checkIn: '2024-03-15', checkOut: '2024-03-20', amount: 850, status: 'confirmed', createdAt: '2024-02-01' },
  { id: 'BK-002', customer: 'María García', email: 'maria@email.com', service: 'Tour Manuel Antonio', vendor: 'Tours Nature', checkIn: '2024-03-18', checkOut: '2024-03-18', amount: 120, status: 'pending', createdAt: '2024-02-02' },
  { id: 'BK-003', customer: 'Robert Brown', email: 'robert@email.com', service: 'Villa Tropical', vendor: 'Rentals CR', checkIn: '2024-03-20', checkOut: '2024-03-25', amount: 1500, status: 'confirmed', createdAt: '2024-02-03' },
  { id: 'BK-004', customer: 'Lisa Johnson', email: 'lisa@email.com', service: 'Tour Volcán Arenal', vendor: 'Adventure Tours', checkIn: '2024-03-10', checkOut: '2024-03-10', amount: 95, status: 'cancelled', createdAt: '2024-02-01' }
])

const statusOptions = [
  { value: 'pending', label: 'Pendiente' },
  { value: 'confirmed', label: 'Confirmada' },
  { value: 'cancelled', label: 'Cancelada' },
  { value: 'refunded', label: 'Reembolsada' },
]

const filterStatus = ref<string>('all')
const filterDate = ref<string>('')
const searchQuery = ref('')

const filteredBookings = computed(() => {
  return bookings.value.filter(b => {
    const matchesStatus = filterStatus.value === 'all' || b.status === filterStatus.value
    const matchesSearch = b.customer.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         b.id.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchesStatus && matchesSearch
  })
})

const statusColors = {
  pending: 'bg-yellow-100 text-yellow-800',
  confirmed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
  refunded: 'bg-gray-100 text-gray-800'
}

const totalRevenue = computed(() => {
  return bookings.value
    .filter(b => b.status === 'confirmed')
    .reduce((sum, b) => sum + b.amount, 0)
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Reservas</h1>
        <p class="mt-1 text-gray-500">Gestión de todas las reservas del sistema</p>
      </div>
      <div class="flex space-x-3">
        <button class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
          Exportar
        </button>
        <button class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
          + Nueva Reserva
        </button>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Total Reservas</div>
        <div class="text-3xl font-bold text-gray-900">{{ bookings.length }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Confirmadas</div>
        <div class="text-3xl font-bold text-green-600">{{ bookings.filter(b => b.status === 'confirmed').length }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Pendientes</div>
        <div class="text-3xl font-bold text-yellow-600">{{ bookings.filter(b => b.status === 'pending').length }}</div>
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
            placeholder="Buscar por ID o cliente..."
            class="w-full px-4 py-2 border border-gray-300 rounded-md"
          />
        </div>
        <UiSelect v-model="filterStatus" :options="statusOptions" placeholder="Todos los estados" />
        <input v-model="filterDate" type="date" class="px-4 py-2 border border-gray-300 rounded-md" />
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cliente</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Servicio</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fechas</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Monto</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="booking in filteredBookings" :key="booking.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">{{ booking.id }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm font-medium text-gray-900">{{ booking.customer }}</div>
              <div class="text-sm text-gray-500">{{ booking.email }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900">{{ booking.service }}</div>
              <div class="text-sm text-gray-500">{{ booking.vendor }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ booking.checkIn }} - {{ booking.checkOut }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
              ${{ booking.amount.toLocaleString() }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="['px-2 py-1 text-xs font-medium rounded-full', statusColors[booking.status]]">
                {{ booking.status }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button class="text-blue-600 hover:text-blue-900 mr-3">Ver</button>
              <button class="text-gray-600 hover:text-gray-900">Editar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

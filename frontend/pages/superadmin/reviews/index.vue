<script setup lang="ts">
/**
 * Reviews Management
 * Moderacion de resenas y calificaciones
 */
import { ref, computed } from 'vue'

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

interface Review {
  id: string
  customer: string
  service: string
  vendor: string
  rating: number
  comment: string
  status: 'pending' | 'approved' | 'rejected'
  createdAt: string
  reported: boolean
}

const reviews = ref<Review[]>([
  { id: '1', customer: 'John Smith', service: 'Hotel Costa Verde', vendor: 'Hoteles CR', rating: 5, comment: 'Excelente servicio y ubicacion', status: 'approved', createdAt: '2024-02-01', reported: false },
  { id: '2', customer: 'Maria Garcia', service: 'Tour Manuel Antonio', vendor: 'Tours CR', rating: 4, comment: 'Muy bueno pero un poco caro', status: 'pending', createdAt: '2024-02-02', reported: false },
  { id: '3', customer: 'Anonymous', service: 'Villa Tropical', vendor: 'Rentals CR', rating: 1, comment: 'Spam content', status: 'rejected', createdAt: '2024-02-03', reported: true }
])

const statusOptions = [
  { value: 'pending', label: 'Pendiente' },
  { value: 'approved', label: 'Aprobada' },
  { value: 'rejected', label: 'Rechazada' },
]

const filterStatus = ref<string>('all')
const showReported = ref<boolean>(false)

const filteredReviews = computed(() => {
  return reviews.value.filter(r => {
    const matchesStatus = filterStatus.value === 'all' || r.status === filterStatus.value
    const matchesReported = !showReported.value || r.reported
    return matchesStatus && matchesReported
  })
})

const statusColors = {
  pending: 'bg-yellow-100 text-yellow-800',
  approved: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800'
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Resenas</h1>
        <p class="mt-1 text-gray-500">Moderacion de resenas y calificaciones</p>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Total Resenas</div>
        <div class="text-3xl font-bold text-gray-900">{{ reviews.length }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Aprobadas</div>
        <div class="text-3xl font-bold text-green-600">{{ reviews.filter(r => r.status === 'approved').length }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Pendientes</div>
        <div class="text-3xl font-bold text-yellow-600">{{ reviews.filter(r => r.status === 'pending').length }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Reportadas</div>
        <div class="text-3xl font-bold text-red-600">{{ reviews.filter(r => r.reported).length }}</div>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex flex-wrap gap-4">
        <UiSelect v-model="filterStatus" :options="statusOptions" placeholder="Todos los estados" />
        <label class="flex items-center space-x-2">
          <input v-model="showReported" type="checkbox" class="rounded border-gray-300" />
          <span>Solo reportadas</span>
        </label>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cliente</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Servicio</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rating</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Comentario</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="review in filteredReviews" :key="review.id">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ review.customer }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900">{{ review.service }}</div>
              <div class="text-sm text-gray-500">{{ review.vendor }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              <span v-for="i in 5" :key="i" :class="i <= review.rating ? 'text-yellow-400' : 'text-gray-300'">★</span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">{{ review.comment }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="['px-2 py-1 text-xs font-medium rounded-full', statusColors[review.status]]">
                {{ review.status }}
              </span>
              <span v-if="review.reported" class="ml-2 px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">!</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button class="text-green-600 hover:text-green-900 mr-2">Aprobar</button>
              <button class="text-red-600 hover:text-red-900">Rechazar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

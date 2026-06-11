<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()

interface Review {
  id: string
  user_name: string
  user_email: string
  property_name?: string
  tour_name?: string
  rating: number
  title?: string
  comment?: string
  is_approved: boolean
  created_at: string
}

const reviews = ref<Review[]>([])
const loading = ref(true)
const filterStatus = ref('all')
const currentPage = ref(1)
const totalPages = ref(1)
const totalItems = ref(0)

const statusOptions = [
  { value: 'all', label: 'Todos' },
  { value: 'approved', label: 'Aprobadas' },
  { value: 'pending', label: 'Pendientes' },
]

const fetchReviews = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: currentPage.value,
      page_size: 20,
    }
    if (filterStatus.value !== 'all') params.status = filterStatus.value

    const response = await api.get('/superadmin/reviews', params)
    reviews.value = response.items || []
    totalPages.value = response.total_pages || 1
    totalItems.value = response.total || 0
  } catch (error) {
    console.error('Error fetching reviews:', error)
    reviews.value = []
  } finally {
    loading.value = false
  }
}

const approveReview = async (review: Review) => {
  try {
    await api.put(`/superadmin/reviews/${review.id}`, { is_approved: true })
    review.is_approved = true
  } catch (error) {
    console.error('Error approving review:', error)
  }
}

const rejectReview = async (review: Review) => {
  try {
    await api.put(`/superadmin/reviews/${review.id}`, { is_approved: false })
    review.is_approved = false
  } catch (error) {
    console.error('Error rejecting review:', error)
  }
}

const deleteReview = async (review: Review) => {
  if (!confirm('Eliminar esta resena?')) return
  try {
    await api.delete(`/superadmin/reviews/${review.id}`)
    reviews.value = reviews.value.filter(r => r.id !== review.id)
  } catch (error) {
    console.error('Error deleting review:', error)
  }
}

const changePage = (page: number) => {
  currentPage.value = page
  fetchReviews()
}

const approvedCount = computed(() => reviews.value.filter(r => r.is_approved).length)
const pendingCount = computed(() => reviews.value.filter(r => !r.is_approved).length)

onMounted(() => {
  fetchReviews()
})

watch(filterStatus, () => {
  currentPage.value = 1
  fetchReviews()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Resenas</h1>
        <p class="mt-1 text-gray-500">Moderacion de resenas y calificaciones</p>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Total Resenas</div>
        <div class="text-3xl font-bold text-gray-900">{{ totalItems }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Aprobadas</div>
        <div class="text-3xl font-bold text-green-600">{{ approvedCount }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Pendientes</div>
        <div class="text-3xl font-bold text-yellow-600">{{ pendingCount }}</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow p-4">
      <UiSelect v-model="filterStatus" :options="statusOptions" />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="bg-white rounded-lg shadow p-12 text-center">
      <div class="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
      <p class="text-gray-500">Cargando resenas...</p>
    </div>

    <div v-else-if="reviews.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <p class="text-gray-400 text-lg">No se encontraron resenas</p>
    </div>

    <!-- Table -->
    <div v-else class="bg-white rounded-lg shadow overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cliente</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Servicio</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rating</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Comentario</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="review in reviews" :key="review.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ review.user_name }}</div>
                <div class="text-sm text-gray-500">{{ review.user_email }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap hidden sm:table-cell">
                <div class="text-sm text-gray-900">{{ review.property_name || review.tour_name || '-' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span v-for="i in 5" :key="i" :class="i <= review.rating ? 'text-yellow-400' : 'text-gray-300'">&#9733;</span>
              </td>
              <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate hidden md:table-cell">{{ review.comment }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="['px-2 py-1 text-xs font-medium rounded-full', review.is_approved ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800']">
                  {{ review.is_approved ? 'Aprobada' : 'Pendiente' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button v-if="!review.is_approved" @click="approveReview(review)" class="text-green-600 hover:text-green-900 mr-2">Aprobar</button>
                <button v-if="review.is_approved" @click="rejectReview(review)" class="text-yellow-600 hover:text-yellow-900 mr-2">Rechazar</button>
                <button @click="deleteReview(review)" class="text-red-600 hover:text-red-900">Eliminar</button>
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
  </div>
</template>

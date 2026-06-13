<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-2xl font-bold">Estadísticas</h1>
        <p class="text-gray-500">Resumen de tu negocio</p>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-500">Cargando...</p>
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
      {{ error }}
    </div>

    <div v-else class="space-y-6">
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="bg-white rounded-xl shadow-sm p-6 border-l-4 border-primary">
          <p class="text-gray-500 text-sm">Total Reservas</p>
          <p class="text-3xl font-bold">{{ analytics?.total_bookings || 0 }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm p-6 border-l-4 border-green-500">
          <p class="text-gray-500 text-sm">Ingresos Totales</p>
          <p class="text-3xl font-bold">${{ (analytics?.total_revenue || 0).toLocaleString() }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm p-6 border-l-4 border-yellow-500">
          <p class="text-gray-500 text-sm">Pendientes</p>
          <p class="text-3xl font-bold">{{ analytics?.pending_bookings || 0 }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm p-6 border-l-4 border-purple-500">
          <p class="text-gray-500 text-sm">Propiedades</p>
          <p class="text-3xl font-bold">{{ analytics?.total_properties || 0 }}</p>
        </div>
      </div>

      <!-- Additional Stats -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white rounded-xl shadow-sm p-6">
          <h3 class="font-bold text-lg mb-4">Tours</h3>
          <p class="text-2xl font-bold text-primary">{{ analytics?.total_tours || 0 }}</p>
          <p class="text-gray-500 text-sm">tours activos</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm p-6">
          <h3 class="font-bold text-lg mb-4">Rating</h3>
          <p class="text-2xl font-bold text-primary">{{ analytics?.rating?.toFixed(1) || '0.0' }} ⭐</p>
          <p class="text-gray-500 text-sm">{{ analytics?.total_reviews || 0 }} reseñas</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'vendor',
  middleware: ['auth']
})

const api = useApi()

const analytics = ref<any>(null)
const loading = ref(true)
const error = ref('')

const fetchAnalytics = async () => {
  loading.value = true
  error.value = ''
  try {
    const data = await api.get<any>('/vendors/me/analytics')
    analytics.value = data
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar analíticas'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchAnalytics()
})
</script>

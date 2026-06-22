<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()
const router = useRouter()

const activeTab = ref<'vehicles' | 'boats'>('vehicles')

const tabs = [
  { key: 'vehicles', label: 'Vehiculos' },
  { key: 'boats', label: 'Botes' },
]

const stats = reactive({
  vehicles: { total: 0, available: 0, unavailable: 0 },
  boats: { total: 0, available: 0, unavailable: 0 },
})
const loading = ref(true)

const fetchStats = async () => {
  loading.value = true
  try {
    const [vehiclesRes, boatsRes] = await Promise.all([
      api.get('/vehicles'),
      api.get('/boats'),
    ])
    const vehicles = Array.isArray(vehiclesRes) ? vehiclesRes : vehiclesRes.items || []
    const boats = Array.isArray(boatsRes) ? boatsRes : boatsRes.items || []

    stats.vehicles.total = vehicles.length
    stats.vehicles.available = vehicles.filter((v: any) => v.is_available).length
    stats.vehicles.unavailable = vehicles.filter((v: any) => !v.is_available).length

    stats.boats.total = boats.length
    stats.boats.available = boats.filter((b: any) => b.is_available).length
    stats.boats.unavailable = boats.filter((b: any) => !b.is_available).length
  } catch (error) {
    console.error('Error fetching fleet stats:', error)
  } finally {
    loading.value = false
  }
}

const navigateTo = (path: string) => {
  router.push(`/superadmin/fleet/${path}`)
}

onMounted(() => {
  fetchStats()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Gestion de Flota</h1>
        <p class="mt-1 text-gray-500">Administra vehiculos y embarcaciones</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key as any"
          :class="[
            activeTab === tab.key
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="bg-white rounded-lg shadow p-12 text-center">
      <UiSpinner size="lg" color="primary" class="mx-auto mb-4" />
      <p class="text-gray-500">Cargando estadisticas...</p>
    </div>

    <template v-else>
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-sm text-gray-500">Total</div>
          <div class="text-3xl font-bold text-gray-900">{{ stats[activeTab].total }}</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-sm text-gray-500">Disponibles</div>
          <div class="text-3xl font-bold text-green-600">{{ stats[activeTab].available }}</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-sm text-gray-500">No Disponibles</div>
          <div class="text-3xl font-bold text-red-600">{{ stats[activeTab].unavailable }}</div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex space-x-4">
        <button
          @click="navigateTo(activeTab)"
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
        >
          Ver {{ tabs.find(t => t.key === activeTab)?.label }}
        </button>
      </div>
    </template>
  </div>
</template>

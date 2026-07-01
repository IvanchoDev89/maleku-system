<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()
const router = useRouter()

const sections = [
  { key: 'vehicles', label: 'Vehículos', icon: 'Car', path: '/superadmin/fleet/vehicles' },
  { key: 'boats', label: 'Botes', icon: 'Ship', path: '/superadmin/fleet/boats' },
  { key: 'transportation', label: 'Transporte', icon: 'Bus', path: '/superadmin/fleet/transportation' },
  { key: 'flights', label: 'Vuelos', icon: 'Plane', path: '/superadmin/fleet/flights' },
]

const statsMap = reactive<Record<string, { total: number; active: number; inactive: number }>>({
  vehicles: { total: 0, active: 0, inactive: 0 },
  boats: { total: 0, active: 0, inactive: 0 },
  transportation: { total: 0, active: 0, inactive: 0 },
  flights: { total: 0, active: 0, inactive: 0 },
})
const loading = ref(true)

const fetchStats = async () => {
  loading.value = true
  try {
    const [vRes, bRes, tRes, fRes] = await Promise.all([
      api.get('/superadmin/listings/vehicles', { page: 1, page_size: 1 }),
      api.get('/superadmin/listings/boats', { page: 1, page_size: 1 }),
      api.get('/superadmin/listings/transportation', { page: 1, page_size: 1 }),
      api.get('/superadmin/listings/flights', { page: 1, page_size: 1 }),
    ])
    statsMap.vehicles = {
      total: vRes.total || 0,
      active: vRes.total || 0,
      inactive: 0,
    }
    statsMap.boats = {
      total: bRes.total || 0,
      active: bRes.total || 0,
      inactive: 0,
    }
    statsMap.transportation = {
      total: tRes.total || 0,
      active: tRes.total || 0,
      inactive: 0,
    }
    statsMap.flights = {
      total: fRes.total || 0,
      active: fRes.total || 0,
      inactive: 0,
    }
  } catch (err) {
    console.error('Error fetching fleet stats:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchStats())
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-3xl font-bold text-gray-900">Gestión de Flota</h1>
      <p class="mt-1 text-gray-500">Administra vehículos, embarcaciones, transporte y vuelos</p>
    </div>

    <div v-if="loading" class="bg-white rounded-lg shadow p-12 text-center">
      <UiSpinner size="lg" color="primary" class="mx-auto mb-4" />
      <p class="text-gray-500">Cargando estadísticas...</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div v-for="section in sections" :key="section.key"
        class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
        @click="router.push(section.path)"
      >
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900">{{ section.label }}</h2>
          <Icon :name="`lucide:${section.icon}`" class="w-6 h-6 text-primary-500" />
        </div>
        <div class="grid grid-cols-3 gap-4 text-center">
          <div>
            <div class="text-2xl font-bold text-gray-900">{{ statsMap[section.key].total }}</div>
            <div class="text-xs text-gray-500">Total</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-green-600">{{ statsMap[section.key].active }}</div>
            <div class="text-xs text-gray-500">Activos</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-red-600">{{ statsMap[section.key].inactive }}</div>
            <div class="text-xs text-gray-500">Inactivos</div>
          </div>
        </div>
        <div class="mt-4 text-sm text-primary-600 font-medium text-center">
          Gestionar {{ section.label.toLowerCase() }} →
        </div>
      </div>
    </div>
  </div>
</template>

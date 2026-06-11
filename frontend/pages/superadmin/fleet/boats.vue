<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()

interface Boat {
  id: string
  vendor_id: string
  equipment_type: string
  brand: string
  model: string
  year: number
  capacity: number
  length_foot: number
  price_per_hour: number
  price_per_day: number
  location: string
  operating_area: string
  requires_license: boolean
  is_available: boolean
  is_active: boolean
  rating: number
  total_reviews: number
}

const boats = ref<Boat[]>([])
const loading = ref(true)
const searchQuery = ref('')
const filterStatus = ref('all')

const statusOptions = [
  { value: 'all', label: 'Todos' },
  { value: 'available', label: 'Disponible' },
  { value: 'unavailable', label: 'No Disponible' },
]

const typeLabels: Record<string, string> = {
  boat: 'Bote',
  jet_ski: 'Jet Ski',
  kayak: 'Kayak',
  paddleboard: 'Paddleboard',
  equipment: 'Equipo',
}

const fetchBoats = async () => {
  loading.value = true
  try {
    const response = await api.get('/boats')
    boats.value = Array.isArray(response) ? response : response.items || []
  } catch (error) {
    console.error('Error fetching boats:', error)
    boats.value = []
  } finally {
    loading.value = false
  }
}

const filteredBoats = computed(() => {
  return boats.value.filter(b => {
    const matchesStatus = filterStatus.value === 'all' ||
      (filterStatus.value === 'available' && b.is_available) ||
      (filterStatus.value === 'unavailable' && !b.is_available)
    const matchesSearch = !searchQuery.value ||
      `${b.brand} ${b.model}`.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      b.location?.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchesStatus && matchesSearch
  })
})

onMounted(() => {
  fetchBoats()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Botes y Embarcaciones</h1>
        <p class="mt-1 text-gray-500">Gestion de botes para tours acuaticos</p>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Total Embarcaciones</div>
        <div class="text-3xl font-bold text-gray-900">{{ boats.length }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Disponibles</div>
        <div class="text-3xl font-bold text-green-600">{{ boats.filter(b => b.is_available).length }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">No Disponibles</div>
        <div class="text-3xl font-bold text-red-600">{{ boats.filter(b => !b.is_available).length }}</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex flex-wrap gap-4">
        <div class="flex-1 min-w-[200px]">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar por marca, modelo o ubicacion..."
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
        <UiSelect v-model="filterStatus" :options="statusOptions" />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="bg-white rounded-lg shadow p-12 text-center">
      <div class="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
      <p class="text-gray-500">Cargando embarcaciones...</p>
    </div>

    <div v-else-if="filteredBoats.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <p class="text-gray-400 text-lg">No se encontraron embarcaciones</p>
    </div>

    <!-- Table -->
    <div v-else class="bg-white rounded-lg shadow overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Embarcacion</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Tipo</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Capacidad</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Ubicacion</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Precio/dia</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="boat in filteredBoats" :key="boat.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ boat.brand }} {{ boat.model }}</div>
                <div class="text-sm text-gray-500">{{ boat.year }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 hidden sm:table-cell">
                {{ typeLabels[boat.equipment_type] || boat.equipment_type }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 hidden sm:table-cell">{{ boat.capacity }} pax</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 hidden md:table-cell">{{ boat.location }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 hidden md:table-cell">${{ boat.price_per_day }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="['px-2 py-1 text-xs font-medium rounded-full', boat.is_available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800']">
                  {{ boat.is_available ? 'Disponible' : 'No Disponible' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

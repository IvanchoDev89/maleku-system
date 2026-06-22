<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()

interface Vehicle {
  id: string
  vendor_id: string
  vehicle_type: string
  brand: string
  model: string
  year: number
  transmission: string
  fuel_type: string
  seats: number
  license_plate: string
  color: string
  price_per_day: number
  location: string
  is_available: boolean
  is_active: boolean
  rating: number
  total_reviews: number
}

const vehicles = ref<Vehicle[]>([])
const loading = ref(true)
const searchQuery = ref('')
const filterStatus = ref('all')
const filterType = ref('all')

const statusOptions = [
  { value: 'all', label: 'Todos' },
  { value: 'available', label: 'Disponible' },
  { value: 'unavailable', label: 'No Disponible' },
]

const typeOptions = [
  { value: 'all', label: 'Todos' },
  { value: 'car', label: 'Auto' },
  { value: 'suv', label: 'SUV' },
  { value: 'van', label: 'Van' },
  { value: 'minibus', label: 'Minibus' },
  { value: 'motorcycle', label: 'Moto' },
]

const statusColors: Record<string, string> = {
  available: 'bg-green-100 text-green-800',
  unavailable: 'bg-red-100 text-red-800',
}

const typeLabels: Record<string, string> = {
  car: 'Auto',
  suv: 'SUV',
  van: 'Van',
  minibus: 'Minibus',
  motorcycle: 'Moto',
}

const fetchVehicles = async () => {
  loading.value = true
  try {
    const response = await api.get('/vehicles')
    vehicles.value = Array.isArray(response) ? response : response.items || []
  } catch (error) {
    console.error('Error fetching vehicles:', error)
    vehicles.value = []
  } finally {
    loading.value = false
  }
}

const filteredVehicles = computed(() => {
  return vehicles.value.filter(v => {
    const matchesStatus = filterStatus.value === 'all' ||
      (filterStatus.value === 'available' && v.is_available) ||
      (filterStatus.value === 'unavailable' && !v.is_available)
    const matchesType = filterType.value === 'all' || v.vehicle_type === filterType.value
    const matchesSearch = !searchQuery.value ||
      `${v.brand} ${v.model}`.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      v.license_plate?.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchesStatus && matchesType && matchesSearch
  })
})

onMounted(() => {
  fetchVehicles()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Vehiculos</h1>
        <p class="mt-1 text-gray-500">Gestion de vehiculos de transporte</p>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Total Vehiculos</div>
        <div class="text-3xl font-bold text-gray-900">{{ vehicles.length }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Disponibles</div>
        <div class="text-3xl font-bold text-green-600">{{ vehicles.filter(v => v.is_available).length }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">No Disponibles</div>
        <div class="text-3xl font-bold text-red-600">{{ vehicles.filter(v => !v.is_available).length }}</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex flex-wrap gap-4">
        <div class="flex-1 min-w-[200px]">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar por marca, modelo o placa..."
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
        <UiSelect v-model="filterStatus" :options="statusOptions" />
        <UiSelect v-model="filterType" :options="typeOptions" />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="bg-white rounded-lg shadow p-12 text-center">
      <UiSpinner size="lg" color="primary" class="mx-auto mb-4" />
      <p class="text-gray-500">Cargando vehiculos...</p>
    </div>

    <!-- Empty -->
    <div v-else-if="filteredVehicles.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <p class="text-gray-400 text-lg">No se encontraron vehiculos</p>
    </div>

    <!-- Table -->
    <div v-else class="bg-white rounded-lg shadow overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vehiculo</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Placa</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Capacidad</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Ubicacion</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Precio/dia</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="vehicle in filteredVehicles" :key="vehicle.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ vehicle.brand }} {{ vehicle.model }}</div>
                <div class="text-sm text-gray-500">{{ vehicle.year }} &middot; {{ vehicle.color }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 hidden sm:table-cell">{{ vehicle.license_plate }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 hidden sm:table-cell">{{ vehicle.seats }} pax</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 hidden md:table-cell">{{ vehicle.location }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 hidden md:table-cell">${{ vehicle.price_per_day }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="['px-2 py-1 text-xs font-medium rounded-full', vehicle.is_available ? statusColors.available : statusColors.unavailable]">
                  {{ vehicle.is_available ? 'Disponible' : 'No Disponible' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Fleet - Vehicles Management
 * Gestión de vehículos de transporte
 */
import { ref, computed } from 'vue'

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

interface Vehicle {
  id: string
  name: string
  type: string
  plate: string
  capacity: number
  status: 'active' | 'maintenance' | 'unavailable'
  vendor: string
  lastMaintenance: string
  nextMaintenance: string
}

const vehicles = ref<Vehicle[]>([
  { id: '1', name: 'Toyota Hiace 2023', type: 'Van', plate: 'CR-1234', capacity: 12, status: 'active', vendor: 'Transportes CR', lastMaintenance: '2024-01-15', nextMaintenance: '2024-04-15' },
  { id: '2', name: 'Hyundai Tucson 2022', type: 'SUV', plate: 'CR-5678', capacity: 5, status: 'active', vendor: 'Rental CR', lastMaintenance: '2024-02-01', nextMaintenance: '2024-05-01' },
  { id: '3', name: 'Mitsubishi L300', type: 'Bus', plate: 'CR-9012', capacity: 25, status: 'maintenance', vendor: 'Transportes CR', lastMaintenance: '2023-12-10', nextMaintenance: '2024-03-10' }
])

const statusOptions = [
  { value: 'active', label: 'Activo' },
  { value: 'maintenance', label: 'Mantenimiento' },
  { value: 'unavailable', label: 'No Disponible' },
]

const typeOptions = [
  { value: 'Van', label: 'Van' },
  { value: 'SUV', label: 'SUV' },
  { value: 'Bus', label: 'Bus' },
  { value: 'Sedan', label: 'Sedan' },
]

const filterStatus = ref<string>('all')
const filterType = ref<string>('all')
const searchQuery = ref('')

const filteredVehicles = computed(() => {
  return vehicles.value.filter(v => {
    const matchesStatus = filterStatus.value === 'all' || v.status === filterStatus.value
    const matchesType = filterType.value === 'all' || v.type === filterType.value
    const matchesSearch = v.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         v.plate.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchesStatus && matchesType && matchesSearch
  })
})

const statusColors = {
  active: 'bg-green-100 text-green-800',
  maintenance: 'bg-yellow-100 text-yellow-800',
  unavailable: 'bg-red-100 text-red-800'
}

const statusLabels = {
  active: 'Activo',
  maintenance: 'Mantenimiento',
  unavailable: 'No Disponible'
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Vehículos</h1>
        <p class="mt-1 text-gray-500">Gestión de vehículos de transporte</p>
      </div>
      <button class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
        + Agregar Vehículo
      </button>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex flex-wrap gap-4">
        <div class="flex-1 min-w-[200px]">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar vehículo..."
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <UiSelect v-model="filterStatus" :options="statusOptions" placeholder="Todos los estados" />
        <UiSelect v-model="filterType" :options="typeOptions" placeholder="Todos los tipos" />
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vehículo</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Placa</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Capacidad</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Proveedor</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Próx. Mant.</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="vehicle in filteredVehicles" :key="vehicle.id">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                  <span class="text-gray-500 text-sm">🚗</span>
                </div>
                <div class="ml-4">
                  <div class="text-sm font-medium text-gray-900">{{ vehicle.name }}</div>
                  <div class="text-sm text-gray-500">{{ vehicle.type }}</div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ vehicle.plate }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ vehicle.capacity }} pax</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="['px-2 py-1 text-xs font-medium rounded-full', statusColors[vehicle.status]]">
                {{ statusLabels[vehicle.status] }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ vehicle.vendor }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ vehicle.nextMaintenance }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button class="text-blue-600 hover:text-blue-900 mr-3">Editar</button>
              <button class="text-gray-600 hover:text-gray-900">Ver</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Fleet - Boats Management
 * Gestión de embarcaciones
 */
import { ref, computed } from 'vue'

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

interface Boat {
  id: string
  name: string
  type: string
  capacity: number
  status: 'active' | 'maintenance' | 'unavailable'
  vendor: string
  location: string
  lastMaintenance: string
}

const boats = ref<Boat[]>([
  { id: '1', name: 'Catamarán del Sol', type: 'Catamarán', capacity: 40, status: 'active', vendor: 'Tours Marítimos CR', location: 'Quepos', lastMaintenance: '2024-01-10' },
  { id: '2', name: 'Yate Coral', type: 'Yate', capacity: 15, status: 'active', vendor: 'Luxury Cruises', location: 'Tamarindo', lastMaintenance: '2024-02-05' },
  { id: '3', name: 'Lancha Express', type: 'Lancha', capacity: 25, status: 'maintenance', vendor: 'Transportes Marinos', location: 'Puntarenas', lastMaintenance: '2023-12-20' }
])

const statusOptions = [
  { value: 'active', label: 'Activo' },
  { value: 'maintenance', label: 'Mantenimiento' },
]

const filterStatus = ref<string>('all')
const searchQuery = ref('')

const filteredBoats = computed(() => {
  return boats.value.filter(b => {
    const matchesStatus = filterStatus.value === 'all' || b.status === filterStatus.value
    const matchesSearch = b.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchesStatus && matchesSearch
  })
})

const statusColors = {
  active: 'bg-green-100 text-green-800',
  maintenance: 'bg-yellow-100 text-yellow-800',
  unavailable: 'bg-red-100 text-red-800'
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Botes y Embarcaciones</h1>
        <p class="mt-1 text-gray-500">Gestión de botes para tours acuáticos</p>
      </div>
      <button class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
        + Agregar Bote
      </button>
    </div>

    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex flex-wrap gap-4">
        <div class="flex-1 min-w-[200px]">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar bote..."
            class="w-full px-4 py-2 border border-gray-300 rounded-md"
          />
        </div>
        <UiSelect v-model="filterStatus" :options="statusOptions" placeholder="Todos los estados" />
      </div>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Bote</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Capacidad</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ubicación</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="boat in filteredBoats" :key="boat.id">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                  <span class="text-blue-500">⛵</span>
                </div>
                <div class="ml-4">
                  <div class="text-sm font-medium text-gray-900">{{ boat.name }}</div>
                  <div class="text-sm text-gray-500">{{ boat.vendor }}</div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ boat.type }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ boat.capacity }} pax</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ boat.location }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="['px-2 py-1 text-xs font-medium rounded-full', statusColors[boat.status]]">
                {{ boat.status }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button class="text-blue-600 hover:text-blue-900 mr-3">Editar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

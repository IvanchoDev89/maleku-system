<script setup lang="ts">
/**
 * Destinations Management
 * Gestion de destinos turisticos
 */
import { ref, computed } from 'vue'

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

interface Destination {
  id: string
  name: string
  type: 'beach' | 'park' | 'city' | 'mountain'
  popularity: number
  activeListings: number
  seoScore: number
}

const destinations = ref<Destination[]>([
  { id: '1', name: 'Manuel Antonio', type: 'beach', popularity: 95, activeListings: 45, seoScore: 88 },
  { id: '2', name: 'Arenal Volcano', type: 'park', popularity: 92, activeListings: 38, seoScore: 85 },
  { id: '3', name: 'Monteverde', type: 'park', popularity: 88, activeListings: 32, seoScore: 82 },
  { id: '4', name: 'Tamarindo', type: 'beach', popularity: 85, activeListings: 56, seoScore: 79 },
  { id: '5', name: 'San Jose', type: 'city', popularity: 70, activeListings: 28, seoScore: 75 }
])

const searchQuery = ref('')

const filteredDestinations = computed(() => {
  return destinations.value.filter(d => 
    d.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const typeLabels = {
  beach: 'Playa',
  park: 'Parque',
  city: 'Ciudad',
  mountain: 'Montana'
}

const typeColors = {
  beach: 'bg-blue-100 text-blue-800',
  park: 'bg-green-100 text-green-800',
  city: 'bg-purple-100 text-purple-800',
  mountain: 'bg-gray-100 text-gray-800'
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Destinos</h1>
        <p class="mt-1 text-gray-500">Gestion de destinos turisticos y SEO</p>
      </div>
      <button class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
        + Agregar Destino
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Total Destinos</div>
        <div class="text-3xl font-bold text-gray-900">{{ destinations.length }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Playas</div>
        <div class="text-3xl font-bold text-blue-600">{{ destinations.filter(d => d.type === 'beach').length }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Parques</div>
        <div class="text-3xl font-bold text-green-600">{{ destinations.filter(d => d.type === 'park').length }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Listings Activos</div>
        <div class="text-3xl font-bold text-gray-900">{{ destinations.reduce((sum, d) => sum + d.activeListings, 0) }}</div>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow p-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Buscar destino..."
        class="w-full md:w-96 px-4 py-2 border border-gray-300 rounded-md"
      />
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Destino</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Popularidad</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Listings</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">SEO Score</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="dest in filteredDestinations" :key="dest.id">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="h-10 w-10 rounded-lg bg-gradient-to-br from-blue-400 to-green-400"></div>
                <div class="ml-4">
                  <div class="text-sm font-medium text-gray-900">{{ dest.name }}</div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="['px-2 py-1 text-xs font-medium rounded-full', typeColors[dest.type]]">
                {{ typeLabels[dest.type] }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                  <div class="bg-blue-500 h-2 rounded-full" :style="{ width: dest.popularity + '%' }"></div>
                </div>
                <span class="text-sm text-gray-900">{{ dest.popularity }}%</span>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ dest.activeListings }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="dest.seoScore >= 80 ? 'text-green-600' : dest.seoScore >= 60 ? 'text-yellow-600' : 'text-red-600'">
                {{ dest.seoScore }}/100
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button class="text-blue-600 hover:text-blue-900 mr-3">Editar</button>
              <button class="text-gray-600 hover:text-gray-900">SEO</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Fleet Management - Main Page
 * Gestión de vehículos, botes, vuelos y equipos
 */
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const router = useRouter()
const activeTab = ref<'vehicles' | 'boats' | 'flights' | 'equipment'>('vehicles')

const tabs = [
  { key: 'vehicles', label: 'Vehículos', icon: 'car' },
  { key: 'boats', label: 'Botes', icon: 'ship' },
  { key: 'flights', label: 'Vuelos', icon: 'plane' },
  { key: 'equipment', label: 'Equipos', icon: 'tools' }
]

const stats = ref({
  vehicles: { total: 45, active: 38, maintenance: 5, unavailable: 2 },
  boats: { total: 23, active: 20, maintenance: 2, unavailable: 1 },
  flights: { total: 8, active: 7, maintenance: 1, unavailable: 0 },
  equipment: { total: 156, available: 134, rented: 18, maintenance: 4 }
})

const navigateTo = (path: string) => {
  router.push(`/superadmin/fleet/${path}`)
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Gestión de Flota</h1>
        <p class="mt-1 text-gray-500">Administra vehículos, botes, vuelos y equipos</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8" aria-label="Tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key as any"
          :class="[
            activeTab === tab.key
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2'
          ]"
        >
          <span>{{ tab.label }}</span>
        </button>
      </nav>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div 
        v-for="(stat, key) in stats[activeTab]" 
        :key="key"
        class="bg-white rounded-lg shadow p-6"
      >
        <div class="text-sm text-gray-500 capitalize">{{ key }}</div>
        <div class="text-3xl font-bold text-gray-900">{{ stat }}</div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex space-x-4">
      <button
        @click="navigateTo(activeTab)"
        class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
      >
        Ver {{ tabs.find(t => t.key === activeTab)?.label }}
      </button>
      <button
        class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
      >
        + Agregar {{ tabs.find(t => t.key === activeTab)?.label.slice(0, -1) }}
      </button>
    </div>

    <!-- Quick Info -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Estado de la Flota</h3>
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <span class="text-gray-600">Mantenimientos Programados</span>
          <span class="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">12</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-gray-600">Alertas de Disponibilidad</span>
          <span class="px-2 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium">3</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-gray-600">Reservas Activas</span>
          <span class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">156</span>
        </div>
      </div>
    </div>
  </div>
</template>

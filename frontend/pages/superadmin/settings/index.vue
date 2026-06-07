<script setup lang="ts">
/**
 * Settings - General Configuration
 * Configuracion global del sistema
 */
import { ref } from 'vue'

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const settings = ref({
  siteName: 'Costa Rica Travel',
  siteUrl: 'https://costaricatravel.dev',
  supportEmail: 'support@costaricatravel.dev',
  defaultCurrency: 'USD',
  commissionRate: 10,
  maintenanceMode: false,
  enableRegistration: true,
  requireEmailVerification: true
})

const currencyOptions = [
  { value: 'USD', label: 'USD' },
  { value: 'CRC', label: 'CRC' },
  { value: 'EUR', label: 'EUR' },
]
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Configuracion Global</h1>
        <p class="mt-1 text-gray-500">Configuracion general del sistema</p>
      </div>
      <button class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
        Guardar Cambios
      </button>
    </div>

    <div class="bg-white rounded-lg shadow p-6 space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label class="block text-sm font-medium text-gray-700">Nombre del Sitio</label>
          <input v-model="settings.siteName" type="text" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">URL del Sitio</label>
          <input v-model="settings.siteUrl" type="url" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Email de Soporte</label>
          <input v-model="settings.supportEmail" type="email" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Moneda por Defecto</label>
          <UiSelect v-model="settings.defaultCurrency" :options="currencyOptions" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Comision (%)</label>
          <input v-model.number="settings.commissionRate" type="number" min="0" max="100" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md" />
        </div>
      </div>

      <div class="border-t border-gray-200 pt-6 space-y-4">
        <h3 class="text-lg font-medium text-gray-900">Opciones del Sistema</h3>
        <div class="flex items-center space-x-3">
          <input v-model="settings.maintenanceMode" type="checkbox" class="h-4 w-4 text-blue-600 rounded" />
          <span class="text-gray-700">Modo Mantenimiento</span>
        </div>
        <div class="flex items-center space-x-3">
          <input v-model="settings.enableRegistration" type="checkbox" class="h-4 w-4 text-blue-600 rounded" />
          <span class="text-gray-700">Permitir Registro de Usuarios</span>
        </div>
        <div class="flex items-center space-x-3">
          <input v-model="settings.requireEmailVerification" type="checkbox" class="h-4 w-4 text-blue-600 rounded" />
          <span class="text-gray-700">Requerir Verificacion de Email</span>
        </div>
      </div>
    </div>
  </div>
</template>

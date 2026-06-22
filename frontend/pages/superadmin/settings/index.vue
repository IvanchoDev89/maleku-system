<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()

const settings = ref<Record<string, any>>({})
const loading = ref(true)
const saving = ref(false)

const settingFields = [
  { key: 'site_name', label: 'Nombre del Sitio', type: 'text' },
  { key: 'site_url', label: 'URL del Sitio', type: 'url' },
  { key: 'support_email', label: 'Email de Soporte', type: 'email' },
  { key: 'default_currency', label: 'Moneda por Defecto', type: 'select', options: [
    { value: 'USD', label: 'USD' },
    { value: 'CRC', label: 'CRC' },
    { value: 'EUR', label: 'EUR' },
  ]},
  { key: 'commission_rate', label: 'Comision (%)', type: 'number' },
]

const systemOptions = [
  { key: 'maintenance_mode', label: 'Modo Mantenimiento' },
  { key: 'enable_registration', label: 'Permitir Registro de Usuarios' },
  { key: 'require_email_verification', label: 'Requerir Verificacion de Email' },
]

const fetchSettings = async () => {
  loading.value = true
  try {
    const response = await api.get('/superadmin/settings')
    settings.value = response.settings || response || {}
  } catch (error) {
    console.error('Error fetching settings:', error)
    settings.value = {}
  } finally {
    loading.value = false
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    await api.put('/superadmin/settings', settings.value)
  } catch (error) {
    console.error('Error saving settings:', error)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchSettings()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Configuracion Global</h1>
        <p class="mt-1 text-gray-500">Configuracion general del sistema</p>
      </div>
      <button
        @click="saveSettings"
        :disabled="saving"
        class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
      >
        {{ saving ? 'Guardando...' : 'Guardar Cambios' }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="bg-white rounded-lg shadow p-12 text-center">
      <UiSpinner size="lg" color="primary" class="mx-auto mb-4" />
      <p class="text-gray-500">Cargando configuracion...</p>
    </div>

    <div v-else class="bg-white rounded-lg shadow p-6 space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div v-for="field in settingFields" :key="field.key">
          <label class="block text-sm font-medium text-gray-700">{{ field.label }}</label>
          <select
            v-if="field.type === 'select'"
            v-model="settings[field.key]"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
          >
            <option v-for="opt in field.options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
          <input
            v-else
            v-model="settings[field.key]"
            :type="field.type"
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      </div>

      <div class="border-t border-gray-200 pt-6 space-y-4">
        <h3 class="text-lg font-medium text-gray-900">Opciones del Sistema</h3>
        <div v-for="opt in systemOptions" :key="opt.key" class="flex items-center space-x-3">
          <input
            v-model="settings[opt.key]"
            type="checkbox"
            class="h-4 w-4 text-primary-600 rounded border-gray-300"
          />
          <span class="text-gray-700">{{ opt.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

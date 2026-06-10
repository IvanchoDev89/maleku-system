<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-2xl font-bold">Configuración</h1>
        <p class="text-gray-500">Administra tu perfil de proveedor</p>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-500">Cargando...</p>
    </div>

    <div v-else class="space-y-6 max-w-3xl">
      <!-- Company Info -->
      <div class="bg-white rounded-xl shadow-sm p-6">
        <h3 class="font-bold text-lg mb-4">Información de la Empresa</h3>
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nombre de Empresa *</label>
            <input v-model="form.business_name" type="text" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Slug *</label>
            <input v-model="form.business_slug" type="text" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tipo de Negocio</label>
            <UiSelect v-model="form.business_type" :options="businessTypeOptions" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
            <textarea v-model="form.description" rows="4" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Dirección</label>
            <input v-model="form.address" type="text" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
              <input v-model="form.phone" type="text" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input v-model="form.email" type="email" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary" />
            </div>
          </div>

          <div class="flex items-center gap-2">
            <input v-model="form.is_active" type="checkbox" class="w-4 h-4 text-primary" />
            <span class="text-sm font-medium text-gray-700">Cuenta activa</span>
          </div>

          <button type="submit" :disabled="saving" class="bg-primary text-white px-6 py-2 rounded-lg hover:bg-primary-dark disabled:opacity-50">
            {{ saving ? 'Guardando...' : 'Guardar Cambios' }}
          </button>
        </form>
      </div>

      <!-- Account Info -->
      <div class="bg-white rounded-xl shadow-sm p-6">
        <h3 class="font-bold text-lg mb-4">Información de la Cuenta</h3>
        <div class="space-y-2 text-sm">
          <p><span class="text-gray-500">Email:</span> {{ user?.email }}</p>
          <p><span class="text-gray-500">Nombre:</span> {{ user?.full_name }}</p>
          <p><span class="text-gray-500">Rol:</span> {{ user?.role }}</p>
          <p><span class="text-gray-500">Creado:</span> {{ formatDate(user?.created_at) }}</p>
        </div>
      </div>
      </div>

      <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        {{ error }}
      </div>

      <div v-if="success" class="bg-green-50 border border-green-200 rounded-lg p-4 text-green-700">
        Configuración guardada exitosamente
      </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'vendor',
  middleware: ['auth']
})

const auth = useAuthStore()
const api = useApi()

const vendor = ref<any>(null)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref(false)

const businessTypeOptions = [
  { value: 'hotel', label: 'Hotel' },
  { value: 'tour_operator', label: 'Operador de Tours' },
  { value: 'restaurant', label: 'Restaurante' },
  { value: 'activity', label: 'Actividad' },
  { value: 'transportation', label: 'Transporte' },
  { value: 'other', label: 'Otro' },
]

const user = computed(() => auth.user)

const form = reactive({
  business_name: '',
  business_slug: '',
  business_type: 'hotel',
  description: '',
  address: '',
  phone: '',
  email: '',
  is_active: true
})

const generateSlug = () => {
  form.business_slug = form.business_name.toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

watch(() => form.business_name, generateSlug)

const fetchVendor = async () => {
  loading.value = true
  try {
    const data = await api.get<any>('/vendors/me/profile')
    vendor.value = data
    Object.assign(form, data)
    form.is_active = data.is_active
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar perfil'
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  saving.value = true
  error.value = ''
  success.value = false
  try {
    await api.put('/vendors/me/profile', form)
    success.value = true
    setTimeout(() => success.value = false, 3000)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar configuración'
  } finally {
    saving.value = false
  }
}

const formatDate = (date: string | undefined) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('es-CR')
}

onMounted(() => {
  fetchVendor()
})
</script>
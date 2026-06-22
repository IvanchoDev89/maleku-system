<template>
  <div>
    <div class="mb-6">
      <button @click="goBack" class="text-gray-500 hover:text-gray-700 flex items-center gap-2 text-sm">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Volver a Destinos
      </button>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">
      <UiSpinner size="lg" color="primary" class="mx-auto mb-4" />
      Cargando destino...
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
      <p class="text-red-600 font-medium">{{ error }}</p>
      <button @click="fetchDestination" class="mt-3 text-sm text-red-600 hover:underline">Reintentar</button>
    </div>

    <div v-else-if="destination" class="max-w-4xl mx-auto space-y-6">
      <div class="flex gap-2 mb-4">
        <button @click="toggleActive" class="px-4 py-2 rounded-xl text-sm font-medium" :class="destination.is_active ? 'bg-yellow-50 text-yellow-700 hover:bg-yellow-100' : 'bg-green-50 text-green-700 hover:bg-green-100'">
          {{ destination.is_active ? 'Desactivar' : 'Activar' }}
        </button>
        <button @click="softDelete" :disabled="deleting" class="px-4 py-2 rounded-xl text-sm font-medium bg-red-50 text-red-700 hover:bg-red-100 disabled:opacity-50">
          {{ deleting ? 'Eliminando...' : 'Eliminar' }}
        </button>
      </div>

      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="aspect-video bg-gray-100 relative">
          <NuxtImg v-if="destination.image" :src="destination.image" :alt="destination.name" class="w-full h-full object-cover" width="800" height="400" format="webp" />
          <div v-else class="w-full h-full flex items-center justify-center text-6xl">🌴</div>
          <div class="absolute top-4 right-4 flex gap-2">
            <span v-if="destination.is_featured" class="px-3 py-1 bg-yellow-100 text-yellow-700 text-xs font-medium rounded-full shadow">Featured</span>
            <span :class="destination.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'" class="px-3 py-1 text-xs font-medium rounded-full shadow">
              {{ destination.is_active ? 'Activo' : 'Inactivo' }}
            </span>
          </div>
        </div>
        <div class="p-6">
          <h1 class="text-2xl font-bold text-gray-900 mb-2">{{ destination.name }}</h1>
          <p class="text-gray-500">{{ destination.description }}</p>

          <div class="grid grid-cols-2 gap-4 mt-6">
            <div class="p-4 bg-gray-50 rounded-xl">
              <p class="text-xs text-gray-400 uppercase font-medium">Slug</p>
              <p class="text-gray-700 font-medium mt-1">{{ destination.slug }}</p>
            </div>
            <div class="p-4 bg-gray-50 rounded-xl">
              <p class="text-xs text-gray-400 uppercase font-medium">Región</p>
              <p class="text-gray-700 font-medium mt-1 capitalize">{{ destination.region || '—' }}</p>
            </div>
            <div class="p-4 bg-gray-50 rounded-xl">
              <p class="text-xs text-gray-400 uppercase font-medium">Posición</p>
                  <p class="text-gray-700 font-medium mt-1">{{ destination.order || 0 }}</p>
            </div>
            <div class="p-4 bg-gray-50 rounded-xl">
              <p class="text-xs text-gray-400 uppercase font-medium">Creado</p>
              <p class="text-gray-700 font-medium mt-1">{{ new Date(destination.created_at).toLocaleDateString('es-CR') }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi()
const toast = useToast()
const route = useRoute()

definePageMeta({
  layout: 'admin',
  middleware: 'auth'
})

const destinationId = computed(() => route.params.id as string)

const destination = ref<any>(null)
const loading = ref(true)
const error = ref('')
const deleting = ref(false)

const goBack = () => navigateTo('/admin/destinations')

const fetchDestination = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await api.get(`/destinations/${destinationId.value}`)
    destination.value = response
  } catch (err: any) {
    error.value = err?.data?.detail || 'Error al cargar el destino'
    toast.error(error.value)
  } finally {
    loading.value = false
  }
}

const softDelete = async () => {
  if (!confirm('¿Eliminar este destino? Se marcará como inactivo.')) return
  deleting.value = true
  try {
    await api.delete(`/destinations/${destinationId.value}`)
    toast.success('Destino eliminado correctamente')
    navigateTo('/admin/destinations')
  } catch (err: any) {
    toast.error(err?.data?.detail || 'Error al eliminar destino')
  } finally {
    deleting.value = false
  }
}

const toggleActive = async () => {
  if (!destination.value) return
  try {
    await api.put(`/destinations/${destinationId.value}`, { is_active: !destination.value.is_active })
    destination.value.is_active = !destination.value.is_active
    toast.success(destination.value.is_active ? 'Destino activado' : 'Destino desactivado')
  } catch (err: any) {
    toast.error('Error al cambiar estado')
  }
}

onMounted(() => {
  fetchDestination()
})
</script>

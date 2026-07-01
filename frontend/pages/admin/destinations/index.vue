<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div class="flex gap-4">
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar destinos..."
            class="pl-11 pr-4 py-2.5 bg-white text-gray-700 rounded-xl border border-gray-200 shadow-sm focus:border-primary focus:ring-2 focus:ring-primary/20 w-64"
            @input="debouncedSearch"
          />
          <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </span>
        </div>

        <UiSelect v-model="filters.is_active" :options="activeFilterOptions" placeholder="Todos" @update:model-value="fetchDestinations" />
      </div>

      <button
        @click="navigateTo('/admin/destinations/new')"
        class="bg-primary hover:bg-primary-700 text-white px-5 py-2.5 rounded-xl font-medium shadow-md hover:shadow-lg transition-all"
      >
        + Nuevo Destino
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-if="loading" class="col-span-full py-12 text-center text-gray-400">
        <UiSpinner size="lg" color="primary" class="mx-auto mb-4" />
        Cargando...
      </div>

      <div v-else-if="destinations.length === 0" class="col-span-full py-12 text-center text-gray-400">
        No hay destinos
      </div>

      <div v-for="dest in destinations" :key="dest.id" class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow">
        <div class="aspect-video bg-gray-100 relative overflow-hidden">
          <NuxtImg v-if="dest.image" :src="dest.image" :alt="dest.name" class="w-full h-full object-cover" width="400" height="200" format="webp" />
          <div v-else class="w-full h-full flex items-center justify-center text-4xl">🌴</div>
          <div class="absolute top-3 right-3 flex gap-2">
            <button @click="editDestination(dest)" class="p-2 bg-white/90 rounded-lg shadow hover:bg-white">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button @click="toggleActive(dest)" class="p-2 bg-white/90 rounded-lg shadow hover:bg-white">
              <svg v-if="dest.is_active" class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              <svg v-else class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
              </svg>
            </button>
          </div>
        </div>
        <div class="p-4">
          <div class="flex items-center gap-2 mb-2">
            <h3 class="font-bold text-gray-900">{{ dest.name }}</h3>
            <span v-if="dest.is_featured" class="px-2 py-0.5 bg-yellow-100 text-yellow-700 text-xs font-medium rounded">Featured</span>
          </div>
          <p class="text-gray-500 text-sm line-clamp-2">{{ dest.description }}</p>
          <div class="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
            <span class="text-sm text-gray-500">Orden: {{ dest.order || 0 }}</span>
            <NuxtLink :to="`/admin/destinations/${dest.id}`" class="text-primary font-medium text-sm hover:underline">
              Ver detalles →
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi()
const toast = useToast()

definePageMeta({
  layout: 'admin',
  middleware: 'auth'
})

const destinations = ref([])
const loading = ref(false)
const searchQuery = ref('')

const activeFilterOptions = [
  { value: 'true', label: 'Activos' },
  { value: 'false', label: 'Inactivos' },
]

const filters = ref({
  is_active: ''
})

const fetchDestinations = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {}
    if (filters.value.is_active) params.is_active = filters.value.is_active
    if (searchQuery.value) params.search = searchQuery.value
    const response = await api.get('/destinations', params)
    destinations.value = Array.isArray(response) ? response : response.items || []
  } catch (error) {
    toast.error('Error al cargar destinos')
  } finally {
    loading.value = false
  }
}

const toggleActive = async (dest: any) => {
  try {
    await api.put(`/destinations/${dest.id}`, { is_active: !dest.is_active })
    dest.is_active = !dest.is_active
    toast.success(dest.is_active ? 'Destino activado' : 'Destino desactivado')
  } catch (error) {
    toast.error('Error al cambiar estado')
  }
}

const editDestination = (dest: any) => {
  navigateTo(`/admin/destinations/${dest.id}`)
}
let searchTimeout: ReturnType<typeof setTimeout> | null = null
onUnmounted(() => clearTimeout(searchTimeout!))

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => fetchDestinations(), 300)
}

onMounted(() => {
  fetchDestinations()
})
</script>

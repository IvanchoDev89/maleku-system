<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()
const { t } = useI18n()

interface Destination {
  id: string
  name: string
  description?: string
  region: string
  province?: string
  is_featured: boolean
  is_active: boolean
}

const destinations = ref<Destination[]>([])
const loading = ref(true)
const searchQuery = ref('')
const showForm = ref(false)
const editingId = ref<string | null>(null)
const saving = ref(false)

const form = reactive({
  name: '',
  description: '',
  region: '',
  province: '',
})

const fetchDestinations = async () => {
  loading.value = true
  try {
    const response = await api.get('/destinations')
    destinations.value = Array.isArray(response) ? response : response.items || []
  } catch (error) {
    console.error('Error fetching destinations:', error)
    destinations.value = []
  } finally {
    loading.value = false
  }
}

const filteredDestinations = computed(() => {
  if (!searchQuery.value) return destinations.value
  const q = searchQuery.value.toLowerCase()
  return destinations.value.filter(d =>
    d.name?.toLowerCase().includes(q) ||
    d.region?.toLowerCase().includes(q)
  )
})

const openCreate = () => {
  editingId.value = null
  form.name = ''
  form.description = ''
  form.region = ''
  form.province = ''
  showForm.value = true
}

const openEdit = (dest: Destination) => {
  editingId.value = dest.id
  form.name = dest.name
  form.description = dest.description || ''
  form.region = dest.region
  form.province = dest.province || ''
  showForm.value = true
}

const saveDestination = async () => {
  saving.value = true
  try {
    if (editingId.value) {
      await api.put(`/destinations/${editingId.value}`, form)
    } else {
      await api.post('/destinations', form)
    }
    showForm.value = false
    await fetchDestinations()
  } catch (error) {
    console.error('Error saving destination:', error)
  } finally {
    saving.value = false
  }
}

const toggleActive = async (dest: Destination) => {
  try {
    await api.put(`/destinations/${dest.id}`, { is_active: !dest.is_active })
    dest.is_active = !dest.is_active
  } catch (error) {
    console.error('Error toggling destination:', error)
  }
}

const deleteDestination = async (dest: Destination) => {
  if (!confirm(`Eliminar destino "${dest.name}"?`)) return
  try {
    await api.delete(`/destinations/${dest.id}`)
    await fetchDestinations()
  } catch (error) {
    console.error('Error deleting destination:', error)
  }
}

const regionColors: Record<string, string> = {
  'Pacic': 'bg-blue-100 text-blue-800',
  'Caribe': 'bg-green-100 text-green-800',
  'Central': 'bg-purple-100 text-purple-800',
  'North': 'bg-yellow-100 text-yellow-800',
}

onMounted(() => {
  fetchDestinations()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Destinos</h1>
        <p class="mt-1 text-gray-500">Gestion de destinos turisticos</p>
      </div>
      <button
        @click="openCreate"
        class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
      >
        + Nuevo Destino
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Total Destinos</div>
        <div class="text-3xl font-bold text-gray-900">{{ destinations.length }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Activos</div>
        <div class="text-3xl font-bold text-green-600">{{ destinations.filter(d => d.is_active).length }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Destacados</div>
        <div class="text-3xl font-bold text-yellow-600">{{ destinations.filter(d => d.is_featured).length }}</div>
      </div>
    </div>

    <!-- Search -->
    <div class="bg-white rounded-lg shadow p-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Buscar destino..."
        class="w-full md:w-96 px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
      />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="bg-white rounded-lg shadow p-12 text-center">
      <div class="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
      <p class="text-gray-500">Cargando destinos...</p>
    </div>

    <!-- Empty -->
    <div v-else-if="filteredDestinations.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <p class="text-gray-400 text-lg">No se encontraron destinos</p>
    </div>

    <!-- Table -->
    <div v-else class="bg-white rounded-lg shadow overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Destino</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Region</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Provincia</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Destacado</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Activo</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="dest in filteredDestinations" :key="dest.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ dest.name }}</div>
                <div class="text-sm text-gray-500 line-clamp-1">{{ dest.description }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap hidden sm:table-cell">
                <span class="px-2 py-1 text-xs font-medium rounded-full bg-primary-100 text-primary-800">
                  {{ dest.region }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 hidden md:table-cell">
                {{ dest.province || '-' }}
              </td>
              <td class="px-6 py-4 text-center">
                <span v-if="dest.is_featured" class="text-yellow-500">&#9733;</span>
                <span v-else class="text-gray-300">&#9734;</span>
              </td>
              <td class="px-6 py-4 text-center">
                <button @click="toggleActive(dest)" :class="dest.is_active ? 'text-green-600' : 'text-gray-300'">
                  {{ dest.is_active ? '●' : '○' }}
                </button>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button @click="openEdit(dest)" class="text-primary-600 hover:text-primary-900 mr-3">Editar</button>
                <button @click="deleteDestination(dest)" class="text-red-600 hover:text-red-900">Eliminar</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <Teleport to="body">
      <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showForm = false">
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-4">{{ editingId ? 'Editar Destino' : 'Nuevo Destino' }}</h2>
          <form @submit.prevent="saveDestination" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Nombre</label>
              <input v-model="form.name" type="text" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Descripcion</label>
              <textarea v-model="form.description" rows="3" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"></textarea>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">Region</label>
                <input v-model="form.region" type="text" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">Provincia</label>
                <input v-model="form.province" type="text" class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
              </div>
            </div>
            <div class="flex justify-end space-x-3 pt-4">
              <button type="button" @click="showForm = false" class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">Cancelar</button>
              <button type="submit" :disabled="saving" class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50">
                {{ saving ? 'Guardando...' : 'Guardar' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

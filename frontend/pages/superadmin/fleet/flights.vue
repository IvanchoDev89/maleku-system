<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()
const toast = useToast()

interface Flight {
  id: string
  airline: string
  flight_number: string
  origin: string
  destination: string
  departure_time: string
  arrival_time: string
  route_type: string
  price: number
  currency: string
  is_active: boolean
  created_at: string
  updated_at: string
}

const items = ref<Flight[]>([])
const loading = ref(true)
const filterStatus = ref('all')
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const totalPages = ref(1)

const statusOptions = [
  { value: 'all', label: 'Todos' },
  { value: 'active', label: 'Activo' },
  { value: 'inactive', label: 'Inactivo' },
]

const statusBadge = (active: boolean) =>
  active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'

const fetch = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = { page: page.value, page_size: pageSize.value }
    if (filterStatus.value !== 'all') params.is_active = filterStatus.value === 'active'
    const res = await api.get('/superadmin/listings/flights', params)
    items.value = res.items || []
    total.value = res.total || 0
    totalPages.value = res.total_pages || 1
  } catch { toast.error('Error al cargar vuelos'); items.value = []
  } finally { loading.value = false }
}

const changePage = (p: number) => { page.value = p; fetch() }

const showModal = ref(false)
const editingId = ref<string | null>(null)
const form = reactive({
  airline: '',
  flight_number: '',
  origin: '',
  destination: '',
  departure_time: '',
  arrival_time: '',
  route_type: 'international',
  price: 0,
  currency: 'USD',
  is_active: true,
})
const saving = ref(false)

const resetForm = () => {
  editingId.value = null
  form.airline = ''
  form.flight_number = ''
  form.origin = ''
  form.destination = ''
  form.departure_time = ''
  form.arrival_time = ''
  form.route_type = 'international'
  form.price = 0
  form.currency = 'USD'
  form.is_active = true
}

const openCreate = () => { resetForm(); showModal.value = true }

const editItem = (f: Flight) => {
  editingId.value = f.id
  form.airline = f.airline || ''
  form.flight_number = f.flight_number || ''
  form.origin = f.origin || ''
  form.destination = f.destination || ''
  form.departure_time = f.departure_time || ''
  form.arrival_time = f.arrival_time || ''
  form.route_type = f.route_type || 'international'
  form.price = f.price || 0
  form.currency = f.currency || 'USD'
  form.is_active = f.is_active
  showModal.value = true
}

const save = async () => {
  if (!form.airline || !form.flight_number) { toast.error('Aerolínea y número de vuelo requeridos'); return }
  saving.value = true
  try {
    if (editingId.value) {
      await api.put(`/superadmin/listings/flights/${editingId.value}`, { ...form })
      toast.success('Vuelo actualizado')
    } else {
      await api.post('/superadmin/listings/flights', { ...form })
      toast.success('Vuelo creado')
    }
    showModal.value = false; fetch()
  } catch { toast.error('Error al guardar') } finally { saving.value = false }
}

const toggleActive = async (f: Flight) => {
  try {
    await api.put(`/superadmin/listings/flights/${f.id}`, { is_active: !f.is_active })
    f.is_active = !f.is_active
    toast.success(f.is_active ? 'Activado' : 'Desactivado')
  } catch { toast.error('Error al cambiar estado') }
}

const showConfirm = ref(false)
const confirmTitle = ref('')
const confirmMessage = ref('')
const confirmLoading = ref(false)
let confirmAction: (() => Promise<void>) | null = null

const openConfirm = (title: string, msg: string, action: () => Promise<void>) => {
  confirmTitle.value = title; confirmMessage.value = msg; confirmAction = action; showConfirm.value = true
}
const executeConfirmAction = async () => {
  if (!confirmAction) return
  confirmLoading.value = true
  try { await confirmAction() } finally { confirmLoading.value = false; showConfirm.value = false }
}

const deleteItem = (f: Flight) => {
  openConfirm('Eliminar vuelo', `¿Eliminar ${f.airline} ${f.flight_number}?`, async () => {
    await api.delete(`/superadmin/listings/flights/${f.id}`)
    toast.success('Vuelo eliminado'); fetch()
  })
}

onMounted(() => fetch())
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Vuelos</h1>
        <p class="mt-1 text-gray-500">Gestión de vuelos</p>
      </div>
      <button @click="openCreate" class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 text-sm font-medium">
        + Nuevo Vuelo
      </button>
    </div>

    <UiCard class="p-4">
      <div class="flex flex-wrap gap-4">
        <UiSelect v-model="filterStatus" :options="statusOptions" @update:model-value="page = 1; fetch()" />
      </div>
    </UiCard>

    <div v-if="loading" class="bg-white rounded-lg shadow p-12 text-center">
      <UiSpinner size="lg" color="primary" class="mx-auto mb-4" />
      <p class="text-gray-500">Cargando vuelos...</p>
    </div>

    <div v-else-if="items.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <p class="text-gray-400 text-lg">No se encontraron vuelos</p>
    </div>

    <UiCard v-else padding="none">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vuelo</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Origen</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Destino</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Ruta</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Precio</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="f in items" :key="f.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ f.airline }}</div>
                <div class="text-sm text-gray-500">{{ f.flight_number }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 hidden sm:table-cell">{{ f.origin }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 hidden sm:table-cell">{{ f.destination }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 hidden md:table-cell">{{ f.route_type === 'international' ? 'Internacional' : 'Doméstico' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 hidden md:table-cell">${{ f.price }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="['px-2 py-1 text-xs font-medium rounded-full', statusBadge(f.is_active)]">{{ f.is_active ? 'Activo' : 'Inactivo' }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                <button @click="editItem(f)" class="text-primary-600 hover:text-primary-800 mr-3">Editar</button>
                <button @click="toggleActive(f)" class="text-yellow-600 hover:text-yellow-800 mr-3">{{ f.is_active ? 'Desactivar' : 'Activar' }}</button>
                <button @click="deleteItem(f)" class="text-red-600 hover:text-red-800">Eliminar</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="totalPages > 1" class="flex items-center justify-between px-6 py-3 border-t">
        <span class="text-sm text-gray-600">Total: {{ total }}</span>
        <div class="flex gap-2">
          <button :disabled="page <= 1" @click="changePage(page - 1)" class="px-3 py-1 border rounded text-sm disabled:opacity-50">Anterior</button>
          <span class="px-3 py-1 text-sm text-gray-600">{{ page }} / {{ totalPages }}</span>
          <button :disabled="page >= totalPages" @click="changePage(page + 1)" class="px-3 py-1 border rounded text-sm disabled:opacity-50">Siguiente</button>
        </div>
      </div>
    </UiCard>

    <UiModal v-model="showModal" :title="editingId ? 'Editar Vuelo' : 'Nuevo Vuelo'" max-width="max-w-2xl">
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Aerolínea</label>
            <input v-model="form.airline" type="text" placeholder="Ej: Copa Airlines"
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Número de vuelo</label>
            <input v-model="form.flight_number" type="text" placeholder="Ej: CM123"
              class="w-full px-4 py-2 border border-gray-300 rounded-md" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Origen</label>
            <input v-model="form.origin" type="text" placeholder="Ej: SJO"
              class="w-full px-4 py-2 border border-gray-300 rounded-md" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Destino</label>
            <input v-model="form.destination" type="text" placeholder="Ej: LAX"
              class="w-full px-4 py-2 border border-gray-300 rounded-md" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Salida</label>
            <input v-model="form.departure_time" type="datetime-local"
              class="w-full px-4 py-2 border border-gray-300 rounded-md" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Llegada</label>
            <input v-model="form.arrival_time" type="datetime-local"
              class="w-full px-4 py-2 border border-gray-300 rounded-md" />
          </div>
        </div>
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tipo de ruta</label>
            <select v-model="form.route_type" class="w-full px-4 py-2 border border-gray-300 rounded-md">
              <option value="international">Internacional</option>
              <option value="domestic">Doméstico</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Precio</label>
            <input v-model="form.price" type="number" min="0" step="0.01"
              class="w-full px-4 py-2 border border-gray-300 rounded-md" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Moneda</label>
            <select v-model="form.currency" class="w-full px-4 py-2 border border-gray-300 rounded-md">
              <option value="USD">USD</option>
              <option value="CRC">CRC</option>
            </select>
          </div>
        </div>
        <label class="flex items-center gap-2">
          <input v-model="form.is_active" type="checkbox" class="rounded border-gray-300" />
          <span class="text-sm text-gray-700">Activo</span>
        </label>
      </div>
      <template #footer>
        <div class="flex justify-end gap-3">
          <button @click="showModal = false" class="px-4 py-2 border border-gray-300 rounded-md text-sm">Cancelar</button>
          <button @click="save" :disabled="saving" class="px-4 py-2 bg-primary-600 text-white rounded-md text-sm hover:bg-primary-700 disabled:opacity-50">
            {{ saving ? 'Guardando...' : editingId ? 'Actualizar' : 'Crear' }}
          </button>
        </div>
      </template>
    </UiModal>

    <UiConfirmDialog v-model="showConfirm" :title="confirmTitle" :message="confirmMessage" confirm-text="Eliminar" variant="danger" :loading="confirmLoading" @confirm="executeConfirmAction" />
  </div>
</template>

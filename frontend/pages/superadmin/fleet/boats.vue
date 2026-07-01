<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()
const toast = useToast()

interface Boat {
  id: string
  vendor_id: string
  name: string
  brand: string
  model: string
  equipment_type: string
  capacity: number
  length_foot: number
  price_per_hour: number
  price_per_day: number
  price_per_week: number
  currency: string
  images: string[]
  features: Record<string, any>
  location: string
  operating_area: string
  requires_license: boolean
  license_notes: string
  is_active: boolean
  created_at: string
  updated_at: string
}

const boats = ref<Boat[]>([])
const loading = ref(true)
const searchQuery = ref('')
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

const typeLabels: Record<string, string> = {
  boat: 'Bote', jet_ski: 'Jet Ski', kayak: 'Kayak',
  paddleboard: 'Paddleboard', equipment: 'Equipo',
}

const statusBadge = (active: boolean) =>
  active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'

const fetchBoats = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = { page: page.value, page_size: pageSize.value }
    if (searchQuery.value) params.search = searchQuery.value
    if (filterStatus.value !== 'all') params.is_active = filterStatus.value === 'active'
    const res = await api.get('/superadmin/listings/boats', params)
    boats.value = res.items || []
    total.value = res.total || 0
    totalPages.value = res.total_pages || 1
  } catch (e) {
    toast.error('Error al cargar embarcaciones')
    boats.value = []
  } finally {
    loading.value = false
  }
}

let searchTimeout: ReturnType<typeof setTimeout>
const onSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => { page.value = 1; fetchBoats() }, 400)
}

const changePage = (p: number) => { page.value = p; fetchBoats() }

const showModal = ref(false)
const editingId = ref<string | null>(null)
const form = reactive({
  vendor_id: '',
  equipment_type: 'boat',
  brand: '',
  model: '',
  year: new Date().getFullYear(),
  capacity: 4,
  length_foot: null as number | null,
  price_per_hour: 0,
  price_per_day: 0,
  price_per_week: 0,
  currency: 'USD',
  location: '',
  operating_area: '',
  requires_license: false,
  license_notes: '',
  is_active: true,
})
const saving = ref(false)

const resetForm = () => {
  editingId.value = null
  form.vendor_id = ''
  form.equipment_type = 'boat'
  form.brand = ''
  form.model = ''
  form.year = new Date().getFullYear()
  form.capacity = 4
  form.length_foot = null
  form.price_per_hour = 0
  form.price_per_day = 0
  form.price_per_week = 0
  form.currency = 'USD'
  form.location = ''
  form.operating_area = ''
  form.requires_license = false
  form.license_notes = ''
  form.is_active = true
}

const openCreate = () => { resetForm(); showModal.value = true }

const editBoat = (b: Boat) => {
  editingId.value = b.id
  form.vendor_id = b.vendor_id || ''
  form.equipment_type = b.equipment_type
  form.brand = b.brand || ''
  form.model = b.model || ''
  form.year = b.year || new Date().getFullYear()
  form.capacity = b.capacity || 4
  form.length_foot = b.length_foot
  form.price_per_hour = b.price_per_hour || 0
  form.price_per_day = b.price_per_day || 0
  form.price_per_week = b.price_per_week || 0
  form.currency = b.currency || 'USD'
  form.location = b.location || ''
  form.operating_area = b.operating_area || ''
  form.requires_license = b.requires_license || false
  form.license_notes = b.license_notes || ''
  form.is_active = b.is_active
  showModal.value = true
}

const saveBoat = async () => {
  if (!form.vendor_id) { toast.error('Vendor ID es requerido'); return }
  saving.value = true
  try {
    if (editingId.value) {
      await api.put(`/superadmin/listings/boats/${editingId.value}`, { ...form })
      toast.success('Embarcación actualizada')
    } else {
      await api.post('/superadmin/listings/boats', { ...form })
      toast.success('Embarcación creada')
    }
    showModal.value = false
    fetchBoats()
  } catch { toast.error('Error al guardar') } finally { saving.value = false }
}

const toggleActive = async (b: Boat) => {
  try {
    const res = await api.patch(`/superadmin/listings/boats/${b.id}/activate`, { is_active: !b.is_active })
    b.is_active = res.is_active
    toast.success(b.is_active ? 'Activada' : 'Desactivada')
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

const deleteBoat = (b: Boat) => {
  openConfirm('Eliminar embarcación', `¿Eliminar ${b.brand || ''} ${b.model || ''}?`, async () => {
    await api.delete(`/superadmin/listings/boats/${b.id}`)
    toast.success('Embarcación eliminada')
    fetchBoats()
  })
}

onMounted(() => fetchBoats())
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Botes y Embarcaciones</h1>
        <p class="mt-1 text-gray-500">Gestión completa de embarcaciones para tours acuáticos</p>
      </div>
      <button @click="openCreate" class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 text-sm font-medium">
        + Nueva Embarcación
      </button>
    </div>

    <UiCard class="p-4">
      <div class="flex flex-wrap gap-4">
        <div class="flex-1 min-w-[200px]">
          <input v-model="searchQuery" type="text" placeholder="Buscar por marca o modelo..." @input="onSearchInput"
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
        </div>
        <UiSelect v-model="filterStatus" :options="statusOptions" @update:model-value="page = 1; fetchBoats()" />
      </div>
    </UiCard>

    <div v-if="loading" class="bg-white rounded-lg shadow p-12 text-center">
      <UiSpinner size="lg" color="primary" class="mx-auto mb-4" />
      <p class="text-gray-500">Cargando embarcaciones...</p>
    </div>

    <div v-else-if="boats.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <p class="text-gray-400 text-lg">No se encontraron embarcaciones</p>
    </div>

    <UiCard v-else padding="none">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Embarcación</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Tipo</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Capacidad</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Ubicación</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Precio/día</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="b in boats" :key="b.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ b.brand || '' }} {{ b.model || '' }}</div>
                <div class="text-sm text-gray-500">{{ b.year || '-' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 hidden sm:table-cell">{{ typeLabels[b.equipment_type] || b.equipment_type }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 hidden sm:table-cell">{{ b.capacity }} pax</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 hidden md:table-cell">{{ b.location || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 hidden md:table-cell">${{ b.price_per_day }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="['px-2 py-1 text-xs font-medium rounded-full', statusBadge(b.is_active)]">{{ b.is_active ? 'Activo' : 'Inactivo' }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                <button @click="editBoat(b)" class="text-primary-600 hover:text-primary-800 mr-3">Editar</button>
                <button @click="toggleActive(b)" class="text-yellow-600 hover:text-yellow-800 mr-3">{{ b.is_active ? 'Desactivar' : 'Activar' }}</button>
                <button @click="deleteBoat(b)" class="text-red-600 hover:text-red-800">Eliminar</button>
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

    <UiModal v-model="showModal" :title="editingId ? 'Editar Embarcación' : 'Nueva Embarcación'" max-width="max-w-2xl">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Vendor ID</label>
          <input v-model="form.vendor_id" type="text" placeholder="UUID del vendor"
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Marca</label>
            <input v-model="form.brand" type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Modelo</label>
            <input v-model="form.model" type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
          </div>
        </div>
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
            <select v-model="form.equipment_type" class="w-full px-4 py-2 border border-gray-300 rounded-md">
              <option value="boat">Bote</option>
              <option value="jet_ski">Jet Ski</option>
              <option value="kayak">Kayak</option>
              <option value="paddleboard">Paddleboard</option>
              <option value="equipment">Equipo</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Año</label>
            <input v-model="form.year" type="number" min="2000" max="2030"
              class="w-full px-4 py-2 border border-gray-300 rounded-md" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Capacidad</label>
            <input v-model="form.capacity" type="number" min="1" max="100"
              class="w-full px-4 py-2 border border-gray-300 rounded-md" />
          </div>
        </div>
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Precio/hora</label>
            <input v-model="form.price_per_hour" type="number" min="0" step="0.01"
              class="w-full px-4 py-2 border border-gray-300 rounded-md" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Precio/día</label>
            <input v-model="form.price_per_day" type="number" min="0" step="0.01"
              class="w-full px-4 py-2 border border-gray-300 rounded-md" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Precio/semana</label>
            <input v-model="form.price_per_week" type="number" min="0" step="0.01"
              class="w-full px-4 py-2 border border-gray-300 rounded-md" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Ubicación</label>
            <input v-model="form.location" type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-md" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Área de operación</label>
            <input v-model="form.operating_area" type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-md" />
          </div>
        </div>
        <div class="flex items-center gap-4">
          <label class="flex items-center gap-2">
            <input v-model="form.requires_license" type="checkbox" class="rounded border-gray-300" />
            <span class="text-sm text-gray-700">Requiere licencia</span>
          </label>
          <label class="flex items-center gap-2">
            <input v-model="form.is_active" type="checkbox" class="rounded border-gray-300" />
            <span class="text-sm text-gray-700">Activo</span>
          </label>
        </div>
      </div>
      <template #footer>
        <div class="flex justify-end gap-3">
          <button @click="showModal = false" class="px-4 py-2 border border-gray-300 rounded-md text-sm">Cancelar</button>
          <button @click="saveBoat" :disabled="saving" class="px-4 py-2 bg-primary-600 text-white rounded-md text-sm hover:bg-primary-700 disabled:opacity-50">
            {{ saving ? 'Guardando...' : editingId ? 'Actualizar' : 'Crear' }}
          </button>
        </div>
      </template>
    </UiModal>

    <UiConfirmDialog v-model="showConfirm" :title="confirmTitle" :message="confirmMessage" confirm-text="Eliminar" variant="danger" :loading="confirmLoading" @confirm="executeConfirmAction" />
  </div>
</template>

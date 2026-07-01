<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()
const toast = useToast()

interface Vehicle {
  id: string
  vendor_id: string
  name: string
  brand: string
  model: string
  vehicle_type: string
  year: number
  transmission: string
  fuel_type: string
  seats: number
  price_per_day: number
  price_per_week: number
  price_per_month: number
  currency: string
  images: string[]
  features: Record<string, any>
  location: string
  is_active: boolean
  is_featured: boolean
  created_at: string
  updated_at: string
}

const vehicles = ref<Vehicle[]>([])
const loading = ref(true)
const searchQuery = ref('')
const filterStatus = ref('all')
const filterType = ref('all')
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const totalPages = ref(1)

const statusOptions = [
  { value: 'all', label: 'Todos' },
  { value: 'active', label: 'Activo' },
  { value: 'inactive', label: 'Inactivo' },
]

const typeOptions = [
  { value: 'all', label: 'Todos' },
  { value: 'car', label: 'Auto' },
  { value: 'suv', label: 'SUV' },
  { value: 'van', label: 'Van' },
  { value: 'minibus', label: 'Minibus' },
  { value: 'motorcycle', label: 'Moto' },
]

const typeLabels: Record<string, string> = {
  car: 'Auto', suv: 'SUV', van: 'Van',
  minibus: 'Minibus', motorcycle: 'Moto',
}

const statusBadge = (active: boolean) =>
  active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'

const fetchVehicles = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = { page: page.value, page_size: pageSize.value }
    if (searchQuery.value) params.search = searchQuery.value
    if (filterType.value !== 'all') params.vehicle_type = filterType.value
    if (filterStatus.value !== 'all') params.is_active = filterStatus.value === 'active'
    const res = await api.get('/superadmin/listings/vehicles', params)
    vehicles.value = res.items || []
    total.value = res.total || 0
    totalPages.value = res.total_pages || 1
  } catch (e) {
    toast.error('Error al cargar vehículos')
    vehicles.value = []
  } finally {
    loading.value = false
  }
}

let searchTimeout: ReturnType<typeof setTimeout>
const onSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    fetchVehicles()
  }, 400)
}

const changePage = (p: number) => {
  page.value = p
  fetchVehicles()
}

// Create / Edit modal
const showModal = ref(false)
const editingId = ref<string | null>(null)
const form = reactive({
  vendor_id: '',
  vehicle_type: 'car',
  brand: '',
  model: '',
  year: new Date().getFullYear(),
  transmission: 'automatic',
  fuel_type: 'gasoline',
  seats: 5,
  price_per_day: 0,
  price_per_week: 0,
  price_per_month: 0,
  currency: 'USD',
  location: '',
  is_active: true,
})
const saving = ref(false)

const resetForm = () => {
  editingId.value = null
  form.vendor_id = ''
  form.vehicle_type = 'car'
  form.brand = ''
  form.model = ''
  form.year = new Date().getFullYear()
  form.transmission = 'automatic'
  form.fuel_type = 'gasoline'
  form.seats = 5
  form.price_per_day = 0
  form.price_per_week = 0
  form.price_per_month = 0
  form.currency = 'USD'
  form.location = ''
  form.is_active = true
}

const openCreate = () => {
  resetForm()
  showModal.value = true
}

const editVehicle = (v: Vehicle) => {
  editingId.value = v.id
  form.vendor_id = v.vendor_id || ''
  form.vehicle_type = v.vehicle_type
  form.brand = v.brand
  form.model = v.model
  form.year = v.year || new Date().getFullYear()
  form.transmission = v.transmission || 'automatic'
  form.fuel_type = v.fuel_type || 'gasoline'
  form.seats = v.seats || 5
  form.price_per_day = v.price_per_day || 0
  form.price_per_week = v.price_per_week || 0
  form.price_per_month = v.price_per_month || 0
  form.currency = v.currency || 'USD'
  form.location = v.location || ''
  form.is_active = v.is_active
  showModal.value = true
}

const saveVehicle = async () => {
  if (!form.brand || !form.model || !form.vendor_id) {
    toast.error('Marca, modelo y vendor son requeridos')
    return
  }
  saving.value = true
  try {
    if (editingId.value) {
      await api.put(`/superadmin/listings/vehicles/${editingId.value}`, { ...form })
      toast.success('Vehículo actualizado')
    } else {
      await api.post('/superadmin/listings/vehicles', { ...form })
      toast.success('Vehículo creado')
    }
    showModal.value = false
    fetchVehicles()
  } catch (e) {
    toast.error('Error al guardar vehículo')
  } finally {
    saving.value = false
  }
}

// Toggle active
const toggleActive = async (v: Vehicle) => {
  try {
    const res = await api.patch(`/superadmin/listings/vehicles/${v.id}/activate`, {
      is_active: !v.is_active,
    })
    v.is_active = res.is_active
    toast.success(v.is_active ? 'Vehículo activado' : 'Vehículo desactivado')
  } catch {
    toast.error('Error al cambiar estado')
  }
}

// Confirm delete
const showConfirm = ref(false)
const confirmTitle = ref('')
const confirmMessage = ref('')
const confirmLoading = ref(false)
let confirmAction: (() => Promise<void>) | null = null

const openConfirm = (title: string, message: string, action: () => Promise<void>) => {
  confirmTitle.value = title
  confirmMessage.value = message
  confirmAction = action
  showConfirm.value = true
}

const executeConfirmAction = async () => {
  if (!confirmAction) return
  confirmLoading.value = true
  try {
    await confirmAction()
  } finally {
    confirmLoading.value = false
    showConfirm.value = false
  }
}

const deleteVehicle = (v: Vehicle) => {
  openConfirm(
    'Eliminar vehículo',
    `¿Estás seguro de eliminar ${v.brand} ${v.model}?`,
    async () => {
      await api.delete(`/superadmin/listings/vehicles/${v.id}`)
      toast.success('Vehículo eliminado')
      fetchVehicles()
    }
  )
}

onMounted(() => {
  fetchVehicles()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Vehículos</h1>
        <p class="mt-1 text-gray-500">Gestión completa de vehículos de transporte</p>
      </div>
      <button @click="openCreate" class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 text-sm font-medium">
        + Nuevo Vehículo
      </button>
    </div>

    <!-- Filters -->
    <UiCard class="p-4">
      <div class="flex flex-wrap gap-4">
        <div class="flex-1 min-w-[200px]">
          <input v-model="searchQuery" type="text" placeholder="Buscar por marca o modelo..." @input="onSearchInput"
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
        </div>
        <UiSelect v-model="filterType" :options="typeOptions" @update:model-value="page = 1; fetchVehicles()" />
        <UiSelect v-model="filterStatus" :options="statusOptions" @update:model-value="page = 1; fetchVehicles()" />
      </div>
    </UiCard>

    <!-- Loading -->
    <div v-if="loading" class="bg-white rounded-lg shadow p-12 text-center">
      <UiSpinner size="lg" color="primary" class="mx-auto mb-4" />
      <p class="text-gray-500">Cargando vehículos...</p>
    </div>

    <!-- Empty -->
    <div v-else-if="vehicles.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <p class="text-gray-400 text-lg">No se encontraron vehículos</p>
    </div>

    <!-- Table -->
    <UiCard v-else padding="none">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vehículo</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Tipo</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Precio/día</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Ubicación</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="v in vehicles" :key="v.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ v.brand }} {{ v.model }}</div>
                <div class="text-sm text-gray-500">{{ v.year }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 hidden sm:table-cell">{{ typeLabels[v.vehicle_type] || v.vehicle_type }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 hidden sm:table-cell">${{ v.price_per_day }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 hidden md:table-cell">{{ v.location || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="['px-2 py-1 text-xs font-medium rounded-full', statusBadge(v.is_active)]">
                  {{ v.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                <button @click="editVehicle(v)" class="text-primary-600 hover:text-primary-800 mr-3">Editar</button>
                <button @click="toggleActive(v)" class="text-yellow-600 hover:text-yellow-800 mr-3">
                  {{ v.is_active ? 'Desactivar' : 'Activar' }}
                </button>
                <button @click="deleteVehicle(v)" class="text-red-600 hover:text-red-800">Eliminar</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex items-center justify-between px-6 py-3 border-t">
        <span class="text-sm text-gray-600">Total: {{ total }}</span>
        <div class="flex gap-2">
          <button :disabled="page <= 1" @click="changePage(page - 1)" class="px-3 py-1 border rounded text-sm disabled:opacity-50">Anterior</button>
          <span class="px-3 py-1 text-sm text-gray-600">{{ page }} / {{ totalPages }}</span>
          <button :disabled="page >= totalPages" @click="changePage(page + 1)" class="px-3 py-1 border rounded text-sm disabled:opacity-50">Siguiente</button>
        </div>
      </div>
    </UiCard>

    <!-- Create/Edit Modal -->
    <UiModal v-model="showModal" :title="editingId ? 'Editar Vehículo' : 'Nuevo Vehículo'" max-width="max-w-2xl">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Vendor ID</label>
          <input v-model="form.vendor_id" type="text" placeholder="UUID del vendor"
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Marca</label>
            <input v-model="form.brand" type="text" placeholder="Ej: Toyota"
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Modelo</label>
            <input v-model="form.model" type="text" placeholder="Ej: Hilux"
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
          </div>
        </div>
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
            <select v-model="form.vehicle_type" class="w-full px-4 py-2 border border-gray-300 rounded-md">
              <option v-for="o in typeOptions.filter(t => t.value !== 'all')" :key="o.value" :value="o.value">{{ o.label }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Año</label>
            <input v-model="form.year" type="number" min="2000" max="2030"
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Asientos</label>
            <input v-model="form.seats" type="number" min="1" max="50"
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
          </div>
        </div>
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Transmisión</label>
            <select v-model="form.transmission" class="w-full px-4 py-2 border border-gray-300 rounded-md">
              <option value="automatic">Automática</option>
              <option value="manual">Manual</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Combustible</label>
            <select v-model="form.fuel_type" class="w-full px-4 py-2 border border-gray-300 rounded-md">
              <option value="gasoline">Gasolina</option>
              <option value="diesel">Diesel</option>
              <option value="electric">Eléctrico</option>
              <option value="hybrid">Híbrido</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Moneda</label>
            <select v-model="form.currency" class="w-full px-4 py-2 border border-gray-300 rounded-md">
              <option value="USD">USD</option>
              <option value="CRC">CRC</option>
            </select>
          </div>
        </div>
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Precio/día</label>
            <input v-model="form.price_per_day" type="number" min="0" step="0.01"
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Precio/semana</label>
            <input v-model="form.price_per_week" type="number" min="0" step="0.01"
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Precio/mes</label>
            <input v-model="form.price_per_month" type="number" min="0" step="0.01"
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Ubicación</label>
          <input v-model="form.location" type="text" placeholder="Ej: San José"
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
        </div>
        <label class="flex items-center gap-2">
          <input v-model="form.is_active" type="checkbox" class="rounded border-gray-300" />
          <span class="text-sm text-gray-700">Activo</span>
        </label>
      </div>
      <template #footer>
        <div class="flex justify-end gap-3">
          <button @click="showModal = false" class="px-4 py-2 border border-gray-300 rounded-md text-sm">Cancelar</button>
          <button @click="saveVehicle" :disabled="saving" class="px-4 py-2 bg-primary-600 text-white rounded-md text-sm hover:bg-primary-700 disabled:opacity-50">
            {{ saving ? 'Guardando...' : editingId ? 'Actualizar' : 'Crear' }}
          </button>
        </div>
      </template>
    </UiModal>

    <!-- Confirm Dialog -->
    <UiConfirmDialog
      v-model="showConfirm"
      :title="confirmTitle"
      :message="confirmMessage"
      confirm-text="Eliminar"
      variant="danger"
      :loading="confirmLoading"
      @confirm="executeConfirmAction"
    />
  </div>
</template>

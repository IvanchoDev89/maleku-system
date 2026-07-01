<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()
const toast = useToast()

interface Transport {
  id: string
  vendor_id: string
  name: string
  description: string
  service_type: string
  vehicle_type: string
  origin: string
  destination: string
  price: number
  currency: string
  pricing_type: string
  schedule: any
  is_active: boolean
  created_at: string
  updated_at: string
}

const items = ref<Transport[]>([])
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

const serviceTypeLabels: Record<string, string> = {
  airport_transfer: 'Traslado Aeropuerto',
  city_tour: 'City Tour',
  custom_route: 'Ruta Personalizada',
  private_transfer: 'Traslado Privado',
}

const statusBadge = (active: boolean) =>
  active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'

const fetch = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = { page: page.value, page_size: pageSize.value }
    if (filterStatus.value !== 'all') params.is_active = filterStatus.value === 'active'
    const res = await api.get('/superadmin/listings/transportation', params)
    items.value = res.items || []
    total.value = res.total || 0
    totalPages.value = res.total_pages || 1
  } catch { toast.error('Error al cargar transporte'); items.value = []
  } finally { loading.value = false }
}

const changePage = (p: number) => { page.value = p; fetch() }

const showModal = ref(false)
const editingId = ref<string | null>(null)
const form = reactive({
  vendor_id: '',
  name: '',
  description: '',
  service_type: 'private_transfer',
  vehicle_type: '',
  origin: '',
  destination: '',
  price: 0,
  currency: 'USD',
  pricing_type: 'per_route',
  is_active: true,
})
const saving = ref(false)

const resetForm = () => {
  editingId.value = null
  form.vendor_id = ''
  form.name = ''
  form.description = ''
  form.service_type = 'private_transfer'
  form.vehicle_type = ''
  form.origin = ''
  form.destination = ''
  form.price = 0
  form.currency = 'USD'
  form.pricing_type = 'per_route'
  form.is_active = true
}

const openCreate = () => { resetForm(); showModal.value = true }

const editItem = (t: Transport) => {
  editingId.value = t.id
  Object.assign(form, {
    vendor_id: t.vendor_id || '',
    name: t.name || '',
    description: t.description || '',
    service_type: t.service_type || 'private_transfer',
    vehicle_type: t.vehicle_type || '',
    origin: t.origin || '',
    destination: t.destination || '',
    price: t.price || 0,
    currency: t.currency || 'USD',
    pricing_type: t.pricing_type || 'per_route',
    is_active: t.is_active,
  })
  showModal.value = true
}

const save = async () => {
  if (!form.vendor_id || !form.name) { toast.error('Vendor ID y nombre son requeridos'); return }
  saving.value = true
  try {
    if (editingId.value) {
      await api.put(`/superadmin/listings/transportation/${editingId.value}`, { ...form })
      toast.success('Transporte actualizado')
    } else {
      await api.post('/superadmin/listings/transportation', { ...form })
      toast.success('Transporte creado')
    }
    showModal.value = false; fetch()
  } catch { toast.error('Error al guardar') } finally { saving.value = false }
}

const toggleActive = async (t: Transport) => {
  try {
    const res = await api.patch(`/superadmin/listings/transportation/${t.id}/activate`, { is_active: !t.is_active })
    t.is_active = res.is_active
    toast.success(t.is_active ? 'Activado' : 'Desactivado')
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

const deleteItem = (t: Transport) => {
  openConfirm('Eliminar transporte', `¿Eliminar ${t.name}?`, async () => {
    await api.delete(`/superadmin/listings/transportation/${t.id}`)
    toast.success('Transporte eliminado'); fetch()
  })
}

onMounted(() => fetch())
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Transporte</h1>
        <p class="mt-1 text-gray-500">Gestión de servicios de transporte privado</p>
      </div>
      <button @click="openCreate" class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 text-sm font-medium">
        + Nuevo Transporte
      </button>
    </div>

    <UiCard class="p-4">
      <div class="flex flex-wrap gap-4">
        <UiSelect v-model="filterStatus" :options="statusOptions" @update:model-value="page = 1; fetch()" />
      </div>
    </UiCard>

    <div v-if="loading" class="bg-white rounded-lg shadow p-12 text-center">
      <UiSpinner size="lg" color="primary" class="mx-auto mb-4" />
      <p class="text-gray-500">Cargando transporte...</p>
    </div>

    <div v-else-if="items.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <p class="text-gray-400 text-lg">No se encontraron servicios de transporte</p>
    </div>

    <UiCard v-else padding="none">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nombre</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Tipo Servicio</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Origen</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden sm:table-cell">Destino</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase hidden md:table-cell">Precio</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="t in items" :key="t.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ t.name }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 hidden sm:table-cell">{{ serviceTypeLabels[t.service_type] || t.service_type }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 hidden sm:table-cell">{{ t.origin || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 hidden sm:table-cell">{{ t.destination || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 hidden md:table-cell">${{ t.price }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="['px-2 py-1 text-xs font-medium rounded-full', statusBadge(t.is_active)]">{{ t.is_active ? 'Activo' : 'Inactivo' }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                <button @click="editItem(t)" class="text-primary-600 hover:text-primary-800 mr-3">Editar</button>
                <button @click="toggleActive(t)" class="text-yellow-600 hover:text-yellow-800 mr-3">{{ t.is_active ? 'Desactivar' : 'Activar' }}</button>
                <button @click="deleteItem(t)" class="text-red-600 hover:text-red-800">Eliminar</button>
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

    <UiModal v-model="showModal" :title="editingId ? 'Editar Transporte' : 'Nuevo Transporte'" max-width="max-w-2xl">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Vendor ID</label>
          <input v-model="form.vendor_id" type="text" placeholder="UUID del vendor"
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Nombre del servicio</label>
          <input v-model="form.name" type="text" placeholder="Ej: Traslado Aeropuerto SJO"
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tipo de servicio</label>
            <select v-model="form.service_type" class="w-full px-4 py-2 border border-gray-300 rounded-md">
              <option value="airport_transfer">Traslado Aeropuerto</option>
              <option value="city_tour">City Tour</option>
              <option value="custom_route">Ruta Personalizada</option>
              <option value="private_transfer">Traslado Privado</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tipo de precio</label>
            <select v-model="form.pricing_type" class="w-full px-4 py-2 border border-gray-300 rounded-md">
              <option value="per_route">Por ruta</option>
              <option value="per_hour">Por hora</option>
              <option value="per_day">Por día</option>
            </select>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Origen</label>
            <input v-model="form.origin" type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-md" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Destino</label>
            <input v-model="form.destination" type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-md" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
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
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
          <textarea v-model="form.description" rows="3"
            class="w-full px-4 py-2 border border-gray-300 rounded-md resize-none"></textarea>
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

<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-2xl font-bold">Mis Transportes</h1>
        <p class="text-gray-500">Gestiona tus servicios de transporte privado</p>
      </div>
      <button @click="openCreate" class="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-700">
        + Nuevo Transporte
      </button>
    </div>

    <div v-if="error" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">{{ error }}</div>

    <div v-if="loading" class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-8 space-y-4 animate-pulse">
        <div v-for="i in 5" :key="i" class="h-12 bg-gray-200 rounded" />
      </div>
    </div>

    <div v-else class="bg-white rounded-xl shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Nombre</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600 hidden sm:table-cell">Tipo</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600 hidden md:table-cell">Origen</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600 hidden md:table-cell">Destino</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Precio</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Estado</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="items.length === 0">
              <td colspan="7" class="text-center py-12 text-gray-500">
                No tienes servicios de transporte aún.
                <button @click="openCreate" class="text-primary hover:underline ml-1">Crear primero</button>
              </td>
            </tr>
            <tr v-for="t in items" :key="t.id" class="border-t hover:bg-gray-50">
              <td class="py-3 px-4">
                <div class="font-medium">{{ t.name }}</div>
              </td>
              <td class="py-3 px-4 hidden sm:table-cell">
                <span class="px-2 py-1 bg-gray-100 rounded text-sm">{{ serviceTypeLabels[t.service_type] || t.service_type }}</span>
              </td>
              <td class="py-3 px-4 text-sm hidden md:table-cell">{{ t.origin || '-' }}</td>
              <td class="py-3 px-4 text-sm hidden md:table-cell">{{ t.destination || '-' }}</td>
              <td class="py-3 px-4 font-semibold">${{ t.price }}</td>
              <td class="py-3 px-4">
                <UiBadge :variant="t.is_active ? 'success' : 'danger'">{{ t.is_active ? 'Activo' : 'Inactivo' }}</UiBadge>
              </td>
              <td class="py-3 px-4">
                <button @click="editItem(t)" class="text-primary hover:underline mr-3">Editar</button>
                <button @click="openDeleteDialog(t)" class="text-red-600 hover:underline">Eliminar</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <UiModal v-model="showModal" :title="editingId ? 'Editar Transporte' : 'Nuevo Transporte'" max-width="max-w-2xl">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Nombre del servicio *</label>
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
            <label class="block text-sm font-medium text-gray-700 mb-1">Precio *</label>
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
          <textarea v-model="form.description" rows="3" class="w-full px-4 py-2 border border-gray-300 rounded-md resize-none"></textarea>
        </div>
        <label class="flex items-center gap-2">
          <input v-model="form.is_active" type="checkbox" class="rounded border-gray-300" />
          <span class="text-sm text-gray-700">Activo</span>
        </label>
      </div>
      <template #footer>
        <div class="flex justify-end gap-3">
          <button @click="showModal = false" class="px-4 py-2 border border-gray-300 rounded-md text-sm">Cancelar</button>
          <button @click="saveItem" :disabled="saving" class="px-4 py-2 bg-primary-600 text-white rounded-md text-sm hover:bg-primary-700 disabled:opacity-50">
            {{ saving ? 'Guardando...' : editingId ? 'Actualizar' : 'Crear' }}
          </button>
        </div>
      </template>
    </UiModal>

    <UiConfirmDialog
      :model-value="!!itemToDelete"
      title="Eliminar Transporte"
      :message="`¿Estás seguro de eliminar ${itemToDelete?.name}?`"
      confirm-text="Eliminar"
      variant="danger"
      :loading="deleting"
      @update:model-value="itemToDelete = null"
      @confirm="confirmDelete"
    />
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'vendor',
  middleware: ['auth']
})

const api = useApi()
const toast = useToast()

interface Transport {
  id: string
  name: string
  description: string
  service_type: string
  vehicle_type: string
  origin: string
  destination: string
  price: number
  currency: string
  pricing_type: string
  is_active: boolean
}

const items = ref<Transport[]>([])
const loading = ref(true)
const error = ref('')
const itemToDelete = ref<Transport | null>(null)
const deleting = ref(false)

const serviceTypeLabels: Record<string, string> = {
  airport_transfer: 'Traslado Aeropuerto',
  city_tour: 'City Tour',
  custom_route: 'Ruta Personalizada',
  private_transfer: 'Traslado Privado',
}

const showModal = ref(false)
const editingId = ref<string | null>(null)
const form = reactive({
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

const fetchItems = async () => {
  loading.value = true
  error.value = ''
  try {
    items.value = await api.get<Transport[]>('/transportation/vendor/my-transports')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar transporte'
  } finally {
    loading.value = false
  }
}

const saveItem = async () => {
  if (!form.name) { toast.error('Nombre es requerido'); return }
  saving.value = true
  try {
    if (editingId.value) {
      await api.put(`/transportation/${editingId.value}`, { ...form })
      toast.success('Transporte actualizado')
    } else {
      await api.post('/transportation', { ...form })
      toast.success('Transporte creado')
    }
    showModal.value = false
    fetchItems()
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al guardar')
  } finally {
    saving.value = false
  }
}

const openDeleteDialog = (t: Transport) => { itemToDelete.value = t }

const confirmDelete = async () => {
  if (!itemToDelete.value) return
  deleting.value = true
  try {
    await api.delete(`/transportation/${itemToDelete.value.id}`)
    toast.success('Transporte eliminado')
    itemToDelete.value = null
    fetchItems()
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al eliminar')
  } finally {
    deleting.value = false
  }
}

onMounted(() => fetchItems())
</script>

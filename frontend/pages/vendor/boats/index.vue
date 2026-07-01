<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-2xl font-bold">Mis Embarcaciones</h1>
        <p class="text-gray-500">Gestiona tus botes y equipo náutico</p>
      </div>
      <button @click="openCreate" class="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-700">
        + Nueva Embarcación
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
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Embarcación</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600 hidden sm:table-cell">Tipo</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600 hidden md:table-cell">Capacidad</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600 hidden md:table-cell">Ubicación</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Precio/día</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Estado</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="boats.length === 0">
              <td colspan="7" class="text-center py-12 text-gray-500">
                No tienes embarcaciones aún.
                <button @click="openCreate" class="text-primary hover:underline ml-1">Crear primera</button>
              </td>
            </tr>
            <tr v-for="b in boats" :key="b.id" class="border-t hover:bg-gray-50">
              <td class="py-3 px-4">
                <div class="font-medium">{{ b.brand || '' }} {{ b.model || '' }}</div>
              </td>
              <td class="py-3 px-4 hidden sm:table-cell">
                <span class="px-2 py-1 bg-gray-100 rounded text-sm">{{ typeLabels[b.equipment_type] || b.equipment_type }}</span>
              </td>
              <td class="py-3 px-4 hidden md:table-cell text-sm">{{ b.capacity }} pax</td>
              <td class="py-3 px-4 text-sm hidden md:table-cell">{{ b.location || '-' }}</td>
              <td class="py-3 px-4 font-semibold">${{ b.price_per_day }}</td>
              <td class="py-3 px-4">
                <UiBadge :variant="b.is_active ? 'success' : 'danger'">{{ b.is_active ? 'Activo' : 'Inactivo' }}</UiBadge>
              </td>
              <td class="py-3 px-4">
                <button @click="editBoat(b)" class="text-primary hover:underline mr-3">Editar</button>
                <button @click="openDeleteDialog(b)" class="text-red-600 hover:underline">Eliminar</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <UiModal v-model="showModal" :title="editingId ? 'Editar Embarcación' : 'Nueva Embarcación'" max-width="max-w-2xl">
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Marca</label>
            <input v-model="form.brand" type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Modelo</label>
            <input v-model="form.model" type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-md" />
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
        <label class="flex items-center gap-2">
          <input v-model="form.requires_license" type="checkbox" class="rounded border-gray-300" />
          <span class="text-sm text-gray-700">Requiere licencia</span>
        </label>
        <label class="flex items-center gap-2">
          <input v-model="form.is_active" type="checkbox" class="rounded border-gray-300" />
          <span class="text-sm text-gray-700">Activo</span>
        </label>
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

    <UiConfirmDialog
      :model-value="!!boatToDelete"
      title="Eliminar Embarcación"
      :message="`¿Estás seguro de eliminar ${boatToDelete?.brand || ''} ${boatToDelete?.model || ''}?`"
      confirm-text="Eliminar"
      variant="danger"
      :loading="deleting"
      @update:model-value="boatToDelete = null"
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

interface Boat {
  id: string
  equipment_type: string
  brand: string
  model: string
  year: number
  capacity: number
  length_foot: number
  price_per_hour: number
  price_per_day: number
  price_per_week: number
  location: string
  operating_area: string
  requires_license: boolean
  is_active: boolean
}

const boats = ref<Boat[]>([])
const loading = ref(true)
const error = ref('')
const boatToDelete = ref<Boat | null>(null)
const deleting = ref(false)

const typeLabels: Record<string, string> = {
  boat: 'Bote', jet_ski: 'Jet Ski', kayak: 'Kayak',
  paddleboard: 'Paddleboard', equipment: 'Equipo',
}

const showModal = ref(false)
const editingId = ref<string | null>(null)
const form = reactive({
  equipment_type: 'boat',
  brand: '',
  model: '',
  year: new Date().getFullYear(),
  capacity: 4,
  length_foot: null as number | null,
  price_per_hour: 0,
  price_per_day: 0,
  price_per_week: 0,
  location: '',
  operating_area: '',
  requires_license: false,
  is_active: true,
})
const saving = ref(false)

const resetForm = () => {
  editingId.value = null
  form.equipment_type = 'boat'
  form.brand = ''
  form.model = ''
  form.year = new Date().getFullYear()
  form.capacity = 4
  form.length_foot = null
  form.price_per_hour = 0
  form.price_per_day = 0
  form.price_per_week = 0
  form.location = ''
  form.operating_area = ''
  form.requires_license = false
  form.is_active = true
}

const openCreate = () => { resetForm(); showModal.value = true }

const editBoat = (b: Boat) => {
  editingId.value = b.id
  Object.assign(form, {
    equipment_type: b.equipment_type,
    brand: b.brand || '',
    model: b.model || '',
    year: b.year || new Date().getFullYear(),
    capacity: b.capacity || 4,
    length_foot: b.length_foot,
    price_per_hour: b.price_per_hour || 0,
    price_per_day: b.price_per_day || 0,
    price_per_week: b.price_per_week || 0,
    location: b.location || '',
    operating_area: b.operating_area || '',
    requires_license: b.requires_license || false,
    is_active: b.is_active,
  })
  showModal.value = true
}

const fetchBoats = async () => {
  loading.value = true
  error.value = ''
  try {
    boats.value = await api.get<Boat[]>('/boats/vendor/my-boats')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar embarcaciones'
  } finally {
    loading.value = false
  }
}

const saveBoat = async () => {
  saving.value = true
  try {
    if (editingId.value) {
      await api.put(`/boats/${editingId.value}`, { ...form })
      toast.success('Embarcación actualizada')
    } else {
      await api.post('/boats', { ...form })
      toast.success('Embarcación creada')
    }
    showModal.value = false
    fetchBoats()
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al guardar')
  } finally {
    saving.value = false
  }
}

const openDeleteDialog = (b: Boat) => { boatToDelete.value = b }

const confirmDelete = async () => {
  if (!boatToDelete.value) return
  deleting.value = true
  try {
    await api.delete(`/boats/${boatToDelete.value.id}`)
    toast.success('Embarcación eliminada')
    boatToDelete.value = null
    fetchBoats()
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al eliminar')
  } finally {
    deleting.value = false
  }
}

onMounted(() => fetchBoats())
</script>

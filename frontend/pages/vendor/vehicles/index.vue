<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-2xl font-bold">Mis Vehículos</h1>
        <p class="text-gray-500">Gestiona tu flota de vehículos para alquiler</p>
      </div>
      <button @click="openCreate" class="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-700">
        + Nuevo Vehículo
      </button>
    </div>

    <div v-if="error" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
      {{ error }}
    </div>

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
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Vehículo</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600 hidden sm:table-cell">Tipo</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600 hidden md:table-cell">Año</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600 hidden md:table-cell">Ubicación</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Precio/día</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Estado</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="vehicles.length === 0">
              <td colspan="7" class="text-center py-12 text-gray-500">
                No tienes vehículos aún.
                <button @click="openCreate" class="text-primary hover:underline ml-1">Crear primer vehículo</button>
              </td>
            </tr>
            <tr v-for="v in vehicles" :key="v.id" class="border-t hover:bg-gray-50">
              <td class="py-3 px-4">
                <div class="font-medium">{{ v.brand }} {{ v.model }}</div>
              </td>
              <td class="py-3 px-4 hidden sm:table-cell">
                <span class="px-2 py-1 bg-gray-100 rounded text-sm">{{ typeLabels[v.vehicle_type] || v.vehicle_type }}</span>
              </td>
              <td class="py-3 px-4 hidden md:table-cell text-sm">{{ v.year }}</td>
              <td class="py-3 px-4 text-sm hidden md:table-cell">{{ v.location || '-' }}</td>
              <td class="py-3 px-4 font-semibold">${{ v.price_per_day }}</td>
              <td class="py-3 px-4">
                <UiBadge :variant="v.is_active ? 'success' : 'danger'">
                  {{ v.is_active ? 'Activo' : 'Inactivo' }}
                </UiBadge>
              </td>
              <td class="py-3 px-4">
                <button @click="editVehicle(v)" class="text-primary hover:underline mr-3">Editar</button>
                <button @click="openDeleteDialog(v)" class="text-red-600 hover:underline">Eliminar</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <UiModal v-model="showModal" :title="editingId ? 'Editar Vehículo' : 'Nuevo Vehículo'" max-width="max-w-2xl">
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Marca *</label>
            <input v-model="form.brand" type="text" placeholder="Ej: Toyota"
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Modelo *</label>
            <input v-model="form.model" type="text" placeholder="Ej: Hilux"
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500" />
          </div>
        </div>
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
            <select v-model="form.vehicle_type" class="w-full px-4 py-2 border border-gray-300 rounded-md">
              <option value="car">Auto</option>
              <option value="suv">SUV</option>
              <option value="van">Van</option>
              <option value="minibus">Minibus</option>
              <option value="motorcycle">Moto</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Año</label>
            <input v-model="form.year" type="number" min="2000" max="2030"
              class="w-full px-4 py-2 border border-gray-300 rounded-md" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Asientos</label>
            <input v-model="form.seats" type="number" min="1" max="50"
              class="w-full px-4 py-2 border border-gray-300 rounded-md" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
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
        </div>
        <div class="grid grid-cols-3 gap-4">
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
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Precio/mes</label>
            <input v-model="form.price_per_month" type="number" min="0" step="0.01"
              class="w-full px-4 py-2 border border-gray-300 rounded-md" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Ubicación</label>
          <input v-model="form.location" type="text" placeholder="Ej: San José"
            class="w-full px-4 py-2 border border-gray-300 rounded-md" />
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

    <!-- Delete Confirmation -->
    <UiConfirmDialog
      :model-value="!!vehicleToDelete"
      title="Eliminar Vehículo"
      :message="`¿Estás seguro de eliminar ${vehicleToDelete?.brand} ${vehicleToDelete?.model}?`"
      confirm-text="Eliminar"
      variant="danger"
      :loading="deleting"
      @update:model-value="vehicleToDelete = null"
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

interface Vehicle {
  id: string
  vehicle_type: string
  brand: string
  model: string
  year: number
  transmission: string
  fuel_type: string
  seats: number
  price_per_day: number
  price_per_week: number
  price_per_month: number
  location: string
  is_active: boolean
}

const vehicles = ref<Vehicle[]>([])
const loading = ref(true)
const error = ref('')
const vehicleToDelete = ref<Vehicle | null>(null)
const deleting = ref(false)

const typeLabels: Record<string, string> = {
  car: 'Auto', suv: 'SUV', van: 'Van',
  minibus: 'Minibus', motorcycle: 'Moto',
}

const showModal = ref(false)
const editingId = ref<string | null>(null)
const form = reactive({
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
  location: '',
  is_active: true,
})
const saving = ref(false)

const resetForm = () => {
  editingId.value = null
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
  form.location = ''
  form.is_active = true
}

const openCreate = () => { resetForm(); showModal.value = true }

const editVehicle = (v: Vehicle) => {
  editingId.value = v.id
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
  form.location = v.location || ''
  form.is_active = v.is_active
  showModal.value = true
}

const fetchVehicles = async () => {
  loading.value = true
  error.value = ''
  try {
    vehicles.value = await api.get<Vehicle[]>('/vehicles/vendor/my-vehicles')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar vehículos'
  } finally {
    loading.value = false
  }
}

const saveVehicle = async () => {
  if (!form.brand || !form.model) { toast.error('Marca y modelo son requeridos'); return }
  saving.value = true
  try {
    if (editingId.value) {
      await api.put(`/vehicles/${editingId.value}`, { ...form })
      toast.success('Vehículo actualizado')
    } else {
      await api.post('/vehicles', { ...form })
      toast.success('Vehículo creado')
    }
    showModal.value = false
    fetchVehicles()
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al guardar')
  } finally {
    saving.value = false
  }
}

const openDeleteDialog = (v: Vehicle) => { vehicleToDelete.value = v }

const confirmDelete = async () => {
  if (!vehicleToDelete.value) return
  deleting.value = true
  try {
    await api.delete(`/vehicles/${vehicleToDelete.value.id}`)
    toast.success('Vehículo eliminado')
    vehicleToDelete.value = null
    fetchVehicles()
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al eliminar')
  } finally {
    deleting.value = false
  }
}

onMounted(() => fetchVehicles())
</script>

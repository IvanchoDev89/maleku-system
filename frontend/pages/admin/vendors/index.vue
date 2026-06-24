<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <div class="flex gap-4">
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar proveedores..."
            class="pl-11 pr-4 py-2.5 bg-white text-gray-700 rounded-xl border border-gray-200 shadow-sm focus:border-primary focus:ring-2 focus:ring-primary/20 w-64"
            @input="debouncedSearch"
          />
          <span class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </span>
        </div>

        <UiSelect v-model="filters.business_type" :options="businessTypeFilterOptions" placeholder="Todos los tipos" @update:model-value="fetchVendors" />

        <UiSelect v-model="filters.is_verified" :options="verifiedFilterOptions" placeholder="Verificación" @update:model-value="fetchVendors" />

        <UiSelect v-model="filters.is_active" :options="activeFilterOptions" placeholder="Estado" @update:model-value="fetchVendors" />
      </div>

      <div class="flex gap-3">
        <button
          @click="exportVendors"
          class="px-4 py-2.5 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 transition-colors flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Exportar
        </button>
      </div>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <table class="w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="text-left p-4 text-gray-500 font-semibold text-sm">Proveedor</th>
            <th class="text-left p-4 text-gray-500 font-semibold text-sm">Tipo</th>
            <th class="text-left p-4 text-gray-500 font-semibold text-sm">Propietario</th>
            <th class="text-left p-4 text-gray-500 font-semibold text-sm">Verificado</th>
            <th class="text-left p-4 text-gray-500 font-semibold text-sm">Estado</th>
            <th class="text-left p-4 text-gray-500 font-semibold text-sm">Rating</th>
            <th class="text-left p-4 text-gray-500 font-semibold text-sm">Registrado</th>
            <th class="text-left p-4 text-gray-500 font-semibold text-sm">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading" class="border-t border-gray-100">
            <td colspan="8" class="p-8 text-center text-gray-400">
              <div class="flex items-center justify-center gap-3">
                <UiSpinner size="sm" color="primary" />
                Cargando...
              </div>
            </td>
          </tr>
          <tr v-else-if="vendors.length === 0" class="border-t border-gray-100">
            <td colspan="8" class="p-8 text-center text-gray-400">
              No hay proveedores registrados
            </td>
          </tr>
          <tr v-for="vendor in vendors" :key="vendor.id" class="border-t border-gray-100 hover:bg-gray-50/50 transition-colors">
            <td class="p-4">
              <div class="flex items-center gap-3">
                <div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center text-primary font-bold text-lg overflow-hidden">
                  <NuxtImg v-if="vendor.logo_url" :src="vendor.logo_url" :alt="vendor.business_name" class="w-full h-full object-cover" width="48" height="48" format="webp" />
                  <span v-else>{{ vendor.business_name.charAt(0).toUpperCase() }}</span>
                </div>
                <div>
                  <p class="text-gray-900 font-semibold">{{ vendor.business_name }}</p>
                  <p class="text-gray-500 text-sm">/{{ vendor.business_slug }}</p>
                </div>
              </div>
            </td>
            <td class="p-4">
              <span class="px-3 py-1.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-700">
                {{ getBusinessTypeLabel(vendor.business_type) }}
              </span>
            </td>
            <td class="p-4">
              <div class="text-gray-900">{{ vendor.owner?.full_name || 'N/A' }}</div>
              <div class="text-gray-500 text-sm">{{ vendor.owner?.email || '' }}</div>
            </td>
            <td class="p-4">
              <button
                @click="toggleVerified(vendor)"
                class="flex items-center gap-2"
                :class="vendor.is_verified ? 'text-green-600' : 'text-gray-400'"
              >
                <svg v-if="vendor.is_verified" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{{ vendor.is_verified ? 'Verificado' : 'Pendiente' }}</span>
              </button>
            </td>
            <td class="p-4">
              <button
                @click="toggleActive(vendor)"
                class="flex items-center gap-2"
              >
                <span class="w-2.5 h-2.5 rounded-full" :class="vendor.is_active ? 'bg-green-500' : 'bg-red-400'"></span>
                <span class="text-gray-700">{{ vendor.is_active ? 'Activo' : 'Inactivo' }}</span>
              </button>
            </td>
            <td class="p-4">
              <div v-if="vendor.rating" class="flex items-center gap-1">
                <svg class="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                <span class="font-medium">{{ vendor.rating.toFixed(1) }}</span>
                <span class="text-gray-400 text-sm">({{ vendor.total_reviews }})</span>
              </div>
              <span v-else class="text-gray-400">Sin rating</span>
            </td>
            <td class="p-4 text-gray-500 text-sm">
              {{ formatDate(vendor.created_at) }}
            </td>
            <td class="p-4">
              <div class="flex gap-2">
                <NuxtLink
                  :to="`/admin/vendors/${vendor.id}`"
                  class="p-2 text-gray-400 hover:text-primary hover:bg-primary/5 rounded-lg transition-colors"
                  title="Ver detalles"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </NuxtLink>
                <button
                  @click="editVendor(vendor)"
                  class="p-2 text-gray-400 hover:text-primary hover:bg-primary/5 rounded-lg transition-colors"
                  title="Editar"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button
                  @click="deleteVendor(vendor)"
                  class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  title="Eliminar"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v4m0-4h4m-2 0v2m-2-4h4m4-4h-4m0 4v4m0-4h-4m0 4v-4m0-4h4" />
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="pagination.total > pagination.limit" class="px-4 py-3 border-t border-gray-100 bg-gray-50 flex items-center justify-between">
        <div class="text-sm text-gray-500">
          Mostrando {{ (pagination.page - 1) * pagination.limit + 1 }} - {{ Math.min(pagination.page * pagination.limit, pagination.total) }} de {{ pagination.total }}
        </div>
        <div class="flex gap-2">
          <button
            @click="changePage(pagination.page - 1)"
            :disabled="!pagination.has_prev"
            class="px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Anterior
          </button>
          <button
            @click="changePage(pagination.page + 1)"
            :disabled="!pagination.has_next"
            class="px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Siguiente
          </button>
        </div>
      </div>
    </div>

    <UiModal v-model="showEditModal" title="Editar Proveedor" max-width="max-w-2xl">
      <form class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Nombre del Negocio</label>
          <input
            v-model="editForm.business_name"
            type="text"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Tipo de Negocio</label>
          <UiSelect v-model="editForm.business_type" :options="businessTypeEditOptions" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
          <textarea
            v-model="editForm.description"
            rows="3"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
          ></textarea>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
            <input
              v-model="editForm.phone"
              type="text"
              class="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              v-model="editForm.email"
              type="email"
              class="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Dirección</label>
          <input
            v-model="editForm.address"
            type="text"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
          />
        </div>
      </form>
      <template #footer>
        <button
          @click="showEditModal = false"
          class="flex-1 px-4 py-2.5 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50"
        >
          Cancelar
        </button>
        <button
          @click="saveVendor"
          :disabled="saving"
          class="flex-1 px-4 py-2.5 bg-primary text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
        >
          {{ saving ? 'Guardando...' : 'Guardar Cambios' }}
        </button>
      </template>
    </UiModal>

    <UiConfirmDialog
      v-model="showDeleteModal"
      title="Eliminar Proveedor"
      :message="`¿Estás seguro de que deseas eliminar ${vendorToDelete?.business_name}? Esta acción no se puede deshacer.`"
      confirm-text="Eliminar"
      cancel-text="Cancelar"
      variant="danger"
      :loading="deleting"
      @confirm="confirmDelete"
    />
  </div>
</template>

<script setup lang="ts">
const api = useApi()
const toast = useToast()

definePageMeta({
  layout: 'admin',
  middleware: 'auth'
})

const vendors = ref([])
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const searchQuery = ref('')
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const vendorToDelete = ref(null)
const editForm = ref({})

const businessTypeFilterOptions = [
  { value: 'hotel', label: 'Hotel' },
  { value: 'tour_operator', label: 'Tour Operador' },
  { value: 'restaurant', label: 'Restaurante' },
  { value: 'transporter', label: 'Transporte' },
  { value: 'activity', label: 'Actividad' },
]

const verifiedFilterOptions = [
  { value: 'true', label: 'Verificados' },
  { value: 'false', label: 'Pendientes' },
]

const activeFilterOptions = [
  { value: 'true', label: 'Activos' },
  { value: 'false', label: 'Inactivos' },
]

const businessTypeEditOptions = [
  { value: 'hotel', label: 'Hotel' },
  { value: 'tour_operator', label: 'Tour Operador' },
  { value: 'restaurant', label: 'Restaurante' },
  { value: 'transporter', label: 'Transporte' },
  { value: 'activity', label: 'Actividad' },
]

const filters = ref({
  business_type: '',
  is_verified: '',
  is_active: ''
})

const pagination = ref({
  page: 1,
  limit: 20,
  total: 0,
  total_pages: 0,
  has_next: false,
  has_prev: false
})

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchVendors()
  }, 300)
}

const getBusinessTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    hotel: 'Hotel',
    tour_operator: 'Tour Operador',
    restaurant: 'Restaurante',
    transporter: 'Transporte',
    activity: 'Actividad'
  }
  return labels[type] || type
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('es-CR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const fetchVendors = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {
      limit: pagination.value.limit,
      offset: (pagination.value.page - 1) * pagination.value.limit
    }

    if (searchQuery.value) params.search = searchQuery.value
    if (filters.value.business_type) params.business_type = filters.value.business_type
    if (filters.value.is_verified) params.is_verified = filters.value.is_verified
    if (filters.value.is_active) params.is_active = filters.value.is_active

    const response = await api.get('/admin/vendors', params)
    vendors.value = response.items
    pagination.value = {
      page: response.page,
      limit: response.limit,
      total: response.total,
      total_pages: response.total_pages,
      has_next: response.has_next,
      has_prev: response.has_prev
    }
  } catch (error) {
    console.error('Error fetching vendors:', error)
  } finally {
    loading.value = false
  }
}

const changePage = (page: number) => {
  pagination.value.page = page
  fetchVendors()
}

const toggleVerified = async (vendor: any) => {
  try {
    await api.put(`/admin/vendors/${vendor.id}/verify`, { is_verified: !vendor.is_verified })
    vendor.is_verified = !vendor.is_verified
    toast.success(vendor.is_verified ? 'Proveedor verificado' : 'Verificación removida')
  } catch (error) {
    toast.error('Error al cambiar verificación')
  }
}

const toggleActive = async (vendor: any) => {
  try {
    await api.put(`/admin/vendors/${vendor.id}/active`, { is_active: !vendor.is_active })
    vendor.is_active = !vendor.is_active
    toast.success(vendor.is_active ? 'Proveedor activado' : 'Proveedor desactivado')
  } catch (error) {
    toast.error('Error al cambiar estado')
  }
}

const editVendor = (vendor: any) => {
  editForm.value = { ...vendor }
  showEditModal.value = true
}

const saveVendor = async () => {
  saving.value = true
  try {
    await api.put(`/admin/vendors/${editForm.value.id}`, {
      business_name: editForm.value.business_name,
      business_type: editForm.value.business_type,
      description: editForm.value.description,
      phone: editForm.value.phone,
      email: editForm.value.email,
      address: editForm.value.address
    })
    showEditModal.value = false
    fetchVendors()
    toast.success('Proveedor actualizado')
  } catch (error) {
    toast.error('Error al guardar proveedor')
  } finally {
    saving.value = false
  }
}

const deleteVendor = (vendor: any) => {
  vendorToDelete.value = vendor
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  deleting.value = true
  try {
    await api.delete(`/admin/vendors/${vendorToDelete.value.id}`)
    showDeleteModal.value = false
    vendorToDelete.value = null
    fetchVendors()
    toast.success('Proveedor eliminado')
  } catch (error) {
    toast.error('Error al eliminar proveedor')
  } finally {
    deleting.value = false
  }
}

const exportVendors = () => {
  const data: string[][] = [['Nombre', 'Tipo', 'Email', 'Teléfono', 'Verificado', 'Activo', 'Rating', 'Fecha']]
  vendors.value.forEach((v: any) => {
    data.push([v.business_name, v.business_type, v.email || '', v.phone || '', String(v.is_verified), String(v.is_active), String(v.rating || 0), formatDate(v.created_at)])
  })
  downloadCSV(data, `proveedores-${new Date().toISOString().split('T')[0]}.csv`)
}

onMounted(() => {
  fetchVendors()
})
</script>

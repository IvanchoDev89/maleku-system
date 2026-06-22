<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Gestión de Propiedades</h1>
        <p class="text-gray-500 mt-1">Moderación, destacados y control de contenido</p>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <UiCard padding="xs">
        <p class="text-sm text-gray-500">Total Propiedades</p>
        <p class="text-2xl font-bold text-gray-900">{{ stats.total }}</p>
      </UiCard>
      <UiCard padding="xs">
        <p class="text-sm text-gray-500">Activas</p>
        <p class="text-2xl font-bold text-green-600">{{ stats.active }}</p>
      </UiCard>
      <UiCard padding="xs">
        <p class="text-sm text-gray-500">Destacadas</p>
        <p class="text-2xl font-bold text-purple-600">{{ stats.featured }}</p>
      </UiCard>
      <UiCard padding="xs">
        <p class="text-sm text-gray-500">Rating Promedio</p>
        <p class="text-2xl font-bold text-amber-600">{{ stats.average_rating || '—' }}</p>
      </UiCard>
    </div>

    <!-- Filters -->
    <UiCard padding="xs">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Buscar</label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="Nombre o descripción..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg"
            @input="debouncedSearch"
          >
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
          <UiSelect v-model="filters.status" :options="statusOptions" placeholder="Todas" @update:model-value="page = 1; loadProperties()" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
          <UiSelect v-model="filters.type" :options="typeOptions" placeholder="Todos" @update:model-value="page = 1; loadProperties()" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Región</label>
          <UiSelect v-model="filters.region" :options="regionOptions" placeholder="Todas" @update:model-value="page = 1; loadProperties()" />
        </div>
      </div>
    </UiCard>

    <!-- Properties Table -->
    <UiCard padding="none" class="overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Propiedad</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vendor</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Precio</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reservas</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="property in properties" :key="property.id" class="hover:bg-gray-50">
              <td class="px-4 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-12 h-12 rounded-lg bg-gray-200 flex items-center justify-center text-gray-400">
                    🏨
                  </div>
                  <div>
                    <div class="flex items-center gap-2">
                      <p class="font-medium text-gray-900">{{ property.name }}</p>
                      <span v-if="property.is_featured" class="px-1.5 py-0.5 bg-purple-100 text-purple-700 text-xs rounded">
                        ⭐
                      </span>
                    </div>
                    <p class="text-xs text-gray-500">{{ property.city }}, {{ property.region }}</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-4">
                <p class="text-sm text-gray-900">{{ property.vendor_name }}</p>
                <p class="text-xs text-gray-500">{{ property.vendor_email }}</p>
              </td>
              <td class="px-4 py-4">
                <UiBadge :variant="statusVariant(property.status)">
                  {{ formatStatus(property.status) }}
                </UiBadge>
              </td>
              <td class="px-4 py-4 text-sm text-gray-600">
                ${{ property.base_price }}/noche
              </td>
              <td class="px-4 py-4 text-sm text-gray-600">
                {{ property.total_bookings }}
              </td>
              <td class="px-4 py-4 text-right">
                <div class="flex items-center justify-end gap-2">
                  <button
                    @click="confirmToggleFeatured(property)"
                    class="p-2 text-purple-600 hover:bg-purple-50 rounded-lg"
                    :title="property.is_featured ? 'Quitar destacado' : 'Destacar'"
                  >
                    {{ property.is_featured ? '💔' : '⭐' }}
                  </button>
                  <button
                    @click="confirmToggleStatus(property)"
                    class="p-2 rounded-lg"
                    :class="property.is_active ? 'text-red-600 hover:bg-red-50' : 'text-green-600 hover:bg-green-50'"
                    :title="property.is_active ? 'Desactivar' : 'Activar'"
                  >
                    {{ property.is_active ? '🚫' : '✅' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="total > pageSize" class="flex items-center justify-between p-4 border-t border-gray-100">
        <p class="text-sm text-gray-500">
          Mostrando {{ (page - 1) * pageSize + 1 }}-{{ Math.min(page * pageSize, total) }} de {{ total }}
        </p>
        <div class="flex gap-1">
          <button
            :disabled="page <= 1"
            class="px-3 py-1.5 text-sm rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            @click="changePage(page - 1)"
          >Anterior</button>
          <button
            v-for="p in totalPages"
            :key="p"
            :class="['px-3 py-1.5 text-sm rounded-lg transition-colors', p === page ? 'bg-primary-600 text-white' : 'border border-gray-200 hover:bg-gray-50']"
            @click="changePage(p)"
          >{{ p }}</button>
          <button
            :disabled="page >= totalPages"
            class="px-3 py-1.5 text-sm rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            @click="changePage(page + 1)"
          >Siguiente</button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-8">
        <div class="flex flex-col items-center gap-2">
          <UiSpinner size="md" color="primary" />
          <span class="text-sm text-gray-500">Cargando...</span>
        </div>
      </div>
    </UiCard>

    <!-- Confirm Dialog -->
    <UiConfirmDialog
      v-model="showConfirm"
      :title="confirmTitle"
      :message="confirmMessage"
      :confirm-text="confirmConfirmText"
      :variant="confirmVariant"
      :loading="confirmLoading"
      @confirm="executeConfirmAction"
    />
  </div>
</template>

<script setup lang="ts">
import { Search, Filter, Plus, MoreVertical, Edit, Trash2, Eye, CheckCircle, XCircle, Star, MapPin, Bed, Bath, Users, DollarSign, Image, BarChart3, HeartOff, Home } from 'lucide-vue-next'

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()

const properties = ref<any[]>([])
const stats = ref({ total: 0, active: 0, featured: 0, pending_review: 0 })

const loading = ref(false)

const showConfirm = ref(false)
const confirmTitle = ref('')
const confirmMessage = ref('')
const confirmConfirmText = ref('Confirmar')
const confirmVariant = ref<'danger' | 'warning' | 'info'>('danger')
const confirmLoading = ref(false)
const confirmAction = ref<(() => Promise<void>) | null>(null)

const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

const filters = ref({
  search: '',
  status: 'all',
  type: '',
  region: '',
})

let searchTimeout: NodeJS.Timeout

const statusOptions = [
  { value: 'all', label: 'Todas' },
  { value: 'active', label: 'Activas' },
  { value: 'inactive', label: 'Inactivas' },
]

const typeOptions = [
  { value: '', label: 'Todos' },
  { value: 'hotel', label: 'Hotel' },
  { value: 'villa', label: 'Villa' },
  { value: 'apartment', label: 'Apartamento' },
  { value: 'tour', label: 'Tour' },
]

const regionOptions = [
  { value: '', label: 'Todas' },
  { value: 'guanacaste', label: 'Guanacaste' },
  { value: 'puntarenas', label: 'Puntarenas' },
  { value: 'san_jose', label: 'San José' },
  { value: 'limon', label: 'Limón' },
]

function openConfirm(title: string, message: string, action: () => Promise<void>, options?: { confirmText?: string, variant?: 'danger' | 'warning' | 'info' }) {
  confirmTitle.value = title
  confirmMessage.value = message
  confirmConfirmText.value = options?.confirmText || 'Confirmar'
  confirmVariant.value = options?.variant || 'danger'
  confirmAction.value = action
  showConfirm.value = true
}

async function executeConfirmAction() {
  if (!confirmAction.value) return
  confirmLoading.value = true
  try {
    await confirmAction.value()
  } finally {
    confirmLoading.value = false
    showConfirm.value = false
    confirmAction.value = null
  }
}

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    loadProperties()
  }, 300)
}

const loadProperties = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.value.status !== 'all') params.status = filters.value.status
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.type) params.property_type = filters.value.type
    if (filters.value.region) params.region = filters.value.region

    const response = await api.get('/properties', params)
    const items = response.items || (Array.isArray(response) ? response : [])
    properties.value = items.map((p: any) => ({
      ...p,
      status: p.is_active ? 'active' : 'inactive',
    }))
    total.value = response.total || properties.value.length
  } catch (error) {
    console.error('Error loading properties:', error)
  } finally {
    loading.value = false
  }
}

const changePage = (p: number) => {
  page.value = p
  loadProperties()
}

const loadStats = async () => {
  try {
    const response = await api.get('/superadmin/dashboard/stats')
    const active = properties.value.filter((p: any) => p.is_active).length
    const featured = properties.value.filter((p: any) => p.is_featured).length
    stats.value = {
      total: response.total_properties || 0,
      active: active || response.total_properties || 0,
      featured,
      pending_review: 0,
      average_rating: response.average_rating,
    }
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

const confirmToggleFeatured = (property: any) => {
  openConfirm(
    property.is_featured ? 'Quitar Destacado' : 'Destacar Propiedad',
    `¿${property.is_featured ? 'Quitar destacado' : 'Destacar'} ${property.name}?`,
    () => executeToggleFeatured(property),
    { confirmText: property.is_featured ? 'Quitar Destacado' : 'Destacar', variant: 'warning' }
  )
}

const executeToggleFeatured = async (property: any) => {
  try {
    await api.put(`/properties/${property.id}`, { is_featured: !property.is_featured })
    await loadProperties()
    await loadStats()
  } catch (error) {
    console.error('Error toggling featured:', error)
  }
}

const confirmApproveProperty = (property: any) => {
  openConfirm(
    'Aprobar Propiedad',
    `¿Aprobar ${property.name}?`,
    () => executeApproveProperty(property),
    { confirmText: 'Aprobar', variant: 'warning' }
  )
}

const executeApproveProperty = async (property: any) => {
  try {
    await api.put(`/properties/${property.id}`, { is_active: true })
    await loadProperties()
    await loadStats()
  } catch (error) {
    console.error('Error approving property:', error)
  }
}

const confirmToggleStatus = (property: any) => {
  const newActive = !property.is_active
  const actionLabel = newActive ? 'Activar' : 'Desactivar'
  openConfirm(
    `${actionLabel} Propiedad`,
    `¿${actionLabel.toLowerCase()} ${property.name}?`,
    () => executeToggleStatus(property),
    { confirmText: actionLabel, variant: 'danger' }
  )
}

const executeToggleStatus = async (property: any) => {
  try {
    await api.put(`/properties/${property.id}`, { is_active: !property.is_active })
    await loadProperties()
    await loadStats()
  } catch (error) {
    console.error('Error toggling status:', error)
  }
}

const formatStatus = (status: string) => {
  const statuses: Record<string, string> = {
    active: 'Activa',
    inactive: 'Inactiva',
  }
  return statuses[status] || status
}

function statusVariant(status: string) {
  const map: Record<string, string> = {
    active: 'success',
    inactive: 'default',
  }
  return (map[status] || 'default') as any
}

onMounted(() => {
  loadProperties()
  loadStats()
})
</script>

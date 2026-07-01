<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Gestión de Proveedores</h1>
        <p class="text-gray-500 mt-1">Aprobación, moderación y análisis de vendors</p>
      </div>
      <div class="flex gap-3">
        <button
          @click="showAnalytics = true"
          class="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-2 text-sm font-medium"
        >
          <BarChart3 class="w-4 h-4" />
          <span>{{ $t('superadmin.vendors.analytics') }}</span>
        </button>
        <NuxtLink
          to="/superadmin/vendors/pending"
          class="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors flex items-center gap-2 text-sm font-medium"
        >
          <Clock class="w-4 h-4" />
          <span>{{ $t('superadmin.vendors.pending') }}</span>
          <span v-if="pendingCount > 0" class="px-2 py-0.5 bg-white/20 rounded-full text-sm">{{ pendingCount }}</span>
        </NuxtLink>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
      <UiCard padding="xs">
        <p class="text-sm text-gray-500 dark:text-gray-400">Total Vendors</p>
        <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ stats.total }}</p>
      </UiCard>
      <UiCard padding="xs">
        <p class="text-sm text-gray-500 dark:text-gray-400">Pendientes</p>
        <p class="text-2xl font-bold text-amber-600">{{ stats.pending }}</p>
      </UiCard>
      <UiCard padding="xs">
        <p class="text-sm text-gray-500 dark:text-gray-400">Activos</p>
        <p class="text-2xl font-bold text-green-600">{{ stats.active }}</p>
      </UiCard>
      <UiCard padding="xs">
        <p class="text-sm text-gray-500 dark:text-gray-400">Suspendidos</p>
        <p class="text-2xl font-bold text-red-600">{{ stats.suspended }}</p>
      </UiCard>
      <UiCard padding="xs">
        <p class="text-sm text-gray-500 dark:text-gray-400">Destacados</p>
        <p class="text-2xl font-bold text-purple-600">{{ stats.featured }}</p>
      </UiCard>
    </div>

    <!-- Filters -->
    <UiCard padding="xs">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Buscar</label>
          <UiInput
            :model-value="filters.search"
            placeholder="Nombre o email..."
            @update:model-value="filters.search = $event; debouncedSearch()"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Estado</label>
          <UiSelect v-model="filters.status" :options="statusOptions" placeholder="Todos" @update:model-value="page = 1; loadVendors()" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Tipo</label>
          <UiSelect v-model="filters.type" :options="typeOptions" placeholder="Todos" @update:model-value="page = 1; loadVendors()" />
        </div>
        <div class="flex items-end pb-1">
          <UiCheckbox
            :model-value="filters.featured_only"
            label="Solo destacados"
            @update:model-value="filters.featured_only = $event; loadVendors()"
          />
        </div>
      </div>
    </UiCard>

    <!-- Vendors Table -->
    <UiTable
      :columns="columns"
      :rows="vendors"
      :loading="loading"
      empty-title="No hay proveedores"
      :empty-description="$t('superadmin.vendors.noVendorsDescription')"
    >
      <template #cell-vendor="{ row }">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center text-primary-600 dark:text-primary-300 shrink-0">
            <Store class="w-5 h-5" />
          </div>
          <div class="min-w-0">
            <div class="flex items-center gap-2">
              <p class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ row.business_name }}</p>
              <span v-if="row.is_featured" class="px-1.5 py-0.5 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 text-xs rounded flex items-center gap-1 shrink-0">
                <Star class="w-3 h-3" />
                {{ $t('superadmin.vendors.featured') }}
              </span>
            </div>
            <p class="text-xs text-gray-500 truncate">{{ row.business_type }} • {{ row.owner_name }}</p>
          </div>
        </div>
      </template>
      <template #cell-status="{ row }">
        <UiBadge :variant="statusVariant(row.status)">
          {{ formatStatus(row.status) }}
        </UiBadge>
      </template>
      <template #cell-rating="{ row }">
        <div class="flex items-center gap-1">
          <Star class="w-4 h-4 text-yellow-400 fill-yellow-400" />
          <span class="text-sm font-medium text-gray-900 dark:text-white">{{ row.rating?.toFixed(1) || '—' }}</span>
        </div>
      </template>
      <template #cell-bookings="{ row }">
        <span class="text-gray-600 dark:text-gray-400">{{ row.total_bookings }}</span>
      </template>
      <template #cell-revenue="{ row }">
        <span class="text-gray-600 dark:text-gray-400 font-medium">${{ formatNumber(row.total_revenue || 0) }}</span>
      </template>
      <template #cell-actions="{ row }">
        <div class="flex items-center justify-end gap-2">
          <button
            v-if="row.status === 'pending'"
            @click.stop="confirmApproveVendor(row)"
            class="p-2 text-green-600 hover:bg-green-50 dark:hover:bg-green-900/30 rounded-lg transition-colors"
            :title="$t('superadmin.vendors.approve')"
          >
            <CheckCircle class="w-5 h-5" />
          </button>
          <button
            v-if="row.status === 'active'"
            @click.stop="confirmToggleFeatured(row)"
            class="p-2 text-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900/30 rounded-lg transition-colors"
            :title="row.is_featured ? $t('superadmin.vendors.unfeature') : $t('superadmin.vendors.feature')"
          >
            <component :is="row.is_featured ? HeartOff : Star" class="w-5 h-5" />
          </button>
          <NuxtLink
            :to="`/superadmin/vendors/${row.id}`"
            class="p-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
            :title="$t('superadmin.vendors.view')"
          >
            <Eye class="w-5 h-5" />
          </NuxtLink>
        </div>
      </template>
      <template #footer>
        <div v-if="total > pageSize" class="flex items-center justify-between">
          <p class="text-sm text-gray-500">
            Mostrando {{ (page - 1) * pageSize + 1 }}-{{ Math.min(page * pageSize, total) }} de {{ total }}
          </p>
          <div class="flex gap-1">
            <button
              :disabled="page <= 1"
              class="px-3 py-1.5 text-sm rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-gray-700 dark:text-gray-300"
              @click="changePage(page - 1)"
            >Anterior</button>
            <button
              v-for="p in totalPages"
              :key="p"
              :class="['px-3 py-1.5 text-sm rounded-lg transition-colors', p === page ? 'bg-primary-600 text-white' : 'border border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300']"
              @click="changePage(p)"
            >{{ p }}</button>
            <button
              :disabled="page >= totalPages"
              class="px-3 py-1.5 text-sm rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-gray-700 dark:text-gray-300"
              @click="changePage(page + 1)"
            >Siguiente</button>
          </div>
        </div>
      </template>
    </UiTable>

    <!-- Analytics Modal -->
    <UiModal v-if="showAnalytics" :model-value="showAnalytics" title="Analytics de Vendors" max-width="max-w-5xl" @update:model-value="showAnalytics = false">
      <div class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="bg-slate-50 dark:bg-gray-800 rounded-xl p-4">
            <p class="text-sm text-gray-500 dark:text-gray-400">Total Vendors</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ analytics.total_vendors }}</p>
          </div>
          <div class="bg-green-50 dark:bg-green-900/20 rounded-xl p-4">
            <p class="text-sm text-gray-500 dark:text-gray-400">Activos</p>
            <p class="text-2xl font-bold text-green-600">{{ analytics.active_vendors }}</p>
          </div>
          <div class="bg-amber-50 dark:bg-amber-900/20 rounded-xl p-4">
            <p class="text-sm text-gray-500 dark:text-gray-400">Pendientes</p>
            <p class="text-2xl font-bold text-amber-600">{{ analytics.pending_approval }}</p>
          </div>
          <div class="bg-red-50 dark:bg-red-900/20 rounded-xl p-4">
            <p class="text-sm text-gray-500 dark:text-gray-400">Suspendidos</p>
            <p class="text-2xl font-bold text-red-600">{{ analytics.suspended_vendors }}</p>
          </div>
        </div>

        <div v-if="analytics.top_performers?.length > 0">
          <h3 class="font-bold text-gray-900 dark:text-white mb-4">Top Performers</h3>
          <div class="space-y-3">
            <div
              v-for="(v, index) in analytics.top_performers.slice(0, 5)"
              :key="v.vendor_id"
              class="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-xl"
            >
              <div
                class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shrink-0"
                :class="index === 0 ? 'bg-yellow-400 text-black' : index === 1 ? 'bg-gray-300 text-black' : index === 2 ? 'bg-amber-600 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'"
              >
                {{ index + 1 }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-medium text-gray-900 dark:text-white truncate">{{ v.vendor_id }}</p>
                <p class="text-sm text-gray-500">{{ v.total_bookings }} reservas</p>
              </div>
              <div class="text-right shrink-0">
                <p class="font-bold text-green-600">${{ formatNumber(v.total_revenue) }}</p>
                <p class="text-sm text-yellow-600 flex items-center gap-1 justify-end">
                  <Star class="w-3 h-3 fill-yellow-400 text-yellow-400" />
                  {{ v.average_rating?.toFixed(1) || '—' }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div v-if="analytics.recent_registrations?.length > 0">
          <h3 class="font-bold text-gray-900 dark:text-white mb-4">Registros Recientes</h3>
          <div class="space-y-2">
            <div
              v-for="v in analytics.recent_registrations"
              :key="v.id"
              class="flex justify-between items-center p-3 border border-gray-200 dark:border-gray-700 rounded-lg"
            >
              <div>
                <p class="font-medium text-gray-900 dark:text-white">{{ v.business_name }}</p>
                <p class="text-sm text-gray-500">{{ v.owner_name }}</p>
              </div>
              <UiBadge :variant="statusVariant(v.status)">{{ formatStatus(v.status) }}</UiBadge>
            </div>
          </div>
        </div>
      </div>
    </UiModal>

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
import { Search, Filter, Download, Plus, MoreVertical, Edit, Trash2, Eye, CheckCircle, XCircle, Star, Store, MapPin, Phone, Mail, Calendar, TrendingUp, Users, DollarSign, Package, BarChart3, HeartOff, Clock, X } from 'lucide-vue-next'

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()

const vendors = ref<any[]>([])
const stats = ref({ total: 0, pending: 0, active: 0, suspended: 0, featured: 0, rejected: 0 })
const pendingCount = ref(0)
const showAnalytics = ref(false)
const analytics = ref<any>({})
const loading = ref(false)

const showConfirm = ref(false)
const confirmTitle = ref('')
const confirmMessage = ref('')
const confirmConfirmText = ref('Confirmar')
const confirmVariant = ref<'danger' | 'warning' | 'info'>('danger')
const confirmLoading = ref(false)
let confirmAction: (() => Promise<void>) | null = null

const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

const columns = [
  { key: 'vendor', label: 'Vendor' },
  { key: 'status', label: 'Estado', align: 'center' as const, width: '100px' },
  { key: 'rating', label: 'Rating', align: 'center' as const, width: '90px', hiddenOnMobile: true },
  { key: 'bookings', label: 'Reservas', align: 'center' as const, width: '90px', hiddenOnMobile: true },
  { key: 'revenue', label: 'Ingresos', align: 'right' as const, width: '120px', hiddenOnMobile: true },
  { key: 'actions', label: 'Acciones', align: 'right' as const },
]

const filters = ref({
  search: '',
  status: 'all',
  type: '',
  featured_only: false,
})

let searchTimeout: NodeJS.Timeout

const statusOptions = [
  { value: 'all', label: 'Todos' },
  { value: 'pending', label: 'Pendientes' },
  { value: 'active', label: 'Activos' },
  { value: 'suspended', label: 'Suspendidos' },
  { value: 'rejected', label: 'Rechazados' },
]

const typeOptions = [
  { value: '', label: 'Todos' },
  { value: 'hotel', label: 'Hotel' },
  { value: 'tour', label: 'Tour' },
  { value: 'transport', label: 'Transporte' },
  { value: 'restaurant', label: 'Restaurante' },
]

function openConfirm(title: string, message: string, action: () => Promise<void>, options?: { confirmText?: string, variant?: 'danger' | 'warning' | 'info' }) {
  confirmTitle.value = title
  confirmMessage.value = message
  confirmConfirmText.value = options?.confirmText || 'Confirmar'
  confirmVariant.value = options?.variant || 'danger'
  confirmAction = action
  showConfirm.value = true
}

async function executeConfirmAction() {
  if (!confirmAction) return
  confirmLoading.value = true
  try {
    await confirmAction()
  } finally {
    confirmLoading.value = false
    showConfirm.value = false
    confirmAction = null
  }
}

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    loadVendors()
  }, 300)
}

const loadVendors = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {
      offset: (page.value - 1) * pageSize.value,
      limit: pageSize.value,
    }
    if (filters.value.status !== 'all') params.status = filters.value.status
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.type) params.business_type = filters.value.type
    if (filters.value.featured_only) params.featured_only = 'true'

    const response = await api.get<any>('/superadmin/vendors', params)
    vendors.value = Array.isArray(response) ? response : (response.items || [])
    total.value = Array.isArray(response) ? response.length : (response.total ?? 0)
  } catch (error) {
    console.error('Error loading vendors:', error)
  } finally {
    loading.value = false
  }
}

const changePage = (p: number) => {
  page.value = p
  loadVendors()
}

const loadStats = async () => {
  try {
    const response = await api.get<{
      total_vendors: number;
      pending_approval: number;
      active_vendors: number;
      suspended_vendors: number;
      rejected_vendors: number;
      recent_registrations?: { is_featured?: boolean }[];
    }>('/superadmin/vendors/analytics/overview?days=30')
    analytics.value = response
    stats.value = {
      total: response.total_vendors,
      pending: response.pending_approval,
      active: response.active_vendors,
      suspended: response.suspended_vendors,
      featured: response.recent_registrations?.filter((v: any) => v.is_featured).length || 0,
      rejected: response.rejected_vendors,
    }
    pendingCount.value = response.pending_approval
    if (filters.value.search || filters.value.status !== 'all' || filters.value.type || filters.value.featured_only) {
    } else if (total.value < response.total_vendors) {
      total.value = response.total_vendors
    }
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

const confirmApproveVendor = (vendor: any) => {
  openConfirm(
    'Aprobar Vendor',
    `¿Aprobar a ${vendor.business_name}?`,
    () => executeApproveVendor(vendor),
    { confirmText: 'Aprobar', variant: 'warning' }
  )
}

const executeApproveVendor = async (vendor: any) => {
  try {
    await api.post(`/superadmin/vendors/${vendor.id}/approval`, {
      action: 'approve',
      reason: 'Approved by Super Admin',
    })
    await loadVendors()
    await loadStats()
  } catch (error) {
    console.error('Error approving vendor:', error)
  }
}

const confirmToggleFeatured = (vendor: any) => {
  const actionLabel = vendor.is_featured ? 'quitar de destacados' : 'destacar'
  openConfirm(
    `${vendor.is_featured ? 'Quitar Destacado' : 'Destacar'} Vendor`,
    `¿${actionLabel} a ${vendor.business_name}?`,
    () => executeToggleFeatured(vendor),
    { confirmText: vendor.is_featured ? 'Quitar Destacado' : 'Destacar', variant: 'warning' }
  )
}

const executeToggleFeatured = async (vendor: any) => {
  try {
    await api.post(`/superadmin/vendors/${vendor.id}/feature`, {
      featured: !vendor.is_featured,
    })
    await loadVendors()
    await loadStats()
  } catch (error) {
    console.error('Error toggling featured:', error)
  }
}

const formatStatus = (status: string) => {
  const statuses: Record<string, string> = {
    pending: 'Pendiente',
    active: 'Activo',
    suspended: 'Suspendido',
    rejected: 'Rechazado',
  }
  return statuses[status] || status
}

function statusVariant(status: string) {
  const map: Record<string, string> = {
    pending: 'warning',
    active: 'success',
    suspended: 'danger',
    rejected: 'default',
  }
  return (map[status] || 'default') as any
}

watch(showAnalytics, (show) => {
  if (show) loadStats()
})

onMounted(() => {
  loadVendors()
  loadStats()
})
</script>

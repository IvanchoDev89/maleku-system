<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Gestión de Proveedores</h1>
        <p class="text-gray-500 mt-1">Aprobación, moderación y análisis de vendors</p>
      </div>
      <div class="flex gap-3">
        <button 
          @click="showAnalytics = true"
          class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
        >
          <BarChart3 class="w-4 h-4" />
          <span>{{ $t('superadmin.vendors.analytics') }}</span>
        </button>
        <NuxtLink 
          to="/superadmin/vendors/pending"
          class="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors flex items-center gap-2"
        >
          <Clock class="w-4 h-4" />
          <span>{{ $t('superadmin.vendors.pending') }}</span>
          <span v-if="pendingCount > 0" class="px-2 py-0.5 bg-white/20 rounded-full text-sm">
            {{ pendingCount }}
          </span>
        </NuxtLink>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">Total Vendors</p>
        <p class="text-2xl font-bold text-gray-900">{{ stats.total }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">Pendientes</p>
        <p class="text-2xl font-bold text-amber-600">{{ stats.pending }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">Activos</p>
        <p class="text-2xl font-bold text-green-600">{{ stats.active }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">Suspendidos</p>
        <p class="text-2xl font-bold text-red-600">{{ stats.suspended }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">Destacados</p>
        <p class="text-2xl font-bold text-purple-600">{{ stats.featured }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Buscar</label>
          <div class="relative">
            <input 
              v-model="filters.search"
              type="text" 
              placeholder="Nombre o email..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg"
              @input="debouncedSearch"
            >
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
          <UiSelect v-model="filters.status" :options="statusOptions" placeholder="Todos" @update:model-value="page = 1; loadVendors()" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
          <UiSelect v-model="filters.type" :options="typeOptions" placeholder="Todos" @update:model-value="page = 1; loadVendors()" />
        </div>
        <div class="flex items-end">
          <label class="flex items-center gap-2 cursor-pointer">
            <input 
              v-model="filters.featured_only" 
              type="checkbox"
              class="w-4 h-4 text-slate-900 rounded border-gray-300"
              @change="loadVendors"
            >
            <span class="text-sm text-gray-700">Solo destacados</span>
          </label>
        </div>
      </div>
    </div>

    <!-- Vendors Table -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Vendor</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rating</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reservas</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ingresos</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="vendor in vendors" :key="vendor.id" class="hover:bg-gray-50">
              <td class="px-4 py-4">
                <div class="flex items-center">
                  <div class="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center text-slate-600">
                    <Store class="w-5 h-5" />
                  </div>
                  <div class="ml-3">
                    <div class="flex items-center gap-2">
                      <p class="text-sm font-medium text-gray-900">{{ vendor.business_name }}</p>
                      <span v-if="vendor.is_featured" class="px-1.5 py-0.5 bg-purple-100 text-purple-700 text-xs rounded flex items-center gap-1">
                        <Star class="w-3 h-3" />
                        {{ $t('superadmin.vendors.featured') }}
                      </span>
                    </div>
                    <p class="text-xs text-gray-500">{{ vendor.business_type }} • {{ vendor.owner_name }}</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-4">
                <UiBadge :variant="statusVariant(vendor.status)">
                  {{ formatStatus(vendor.status) }}
                </UiBadge>
              </td>
              <td class="px-4 py-4">
                <div class="flex items-center gap-1">
                  <Star class="w-4 h-4 text-yellow-400 fill-yellow-400" />
                  <span class="text-sm font-medium">{{ vendor.rating.toFixed(1) }}</span>
                </div>
              </td>
              <td class="px-4 py-4 text-sm text-gray-600">
                {{ vendor.total_bookings }}
              </td>
              <td class="px-4 py-4 text-sm text-gray-600">
                ${{ formatNumber(vendor.total_revenue || 0) }}
              </td>
              <td class="px-4 py-4 text-right">
                <div class="flex items-center justify-end gap-2">
                  <button 
                    v-if="vendor.status === 'pending'"
                    @click="confirmApproveVendor(vendor)"
                    class="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    :title="$t('superadmin.vendors.approve')"
                  >
                    <CheckCircle class="w-5 h-5" />
                  </button>
                  <button 
                    v-if="vendor.status === 'active'"
                    @click="confirmToggleFeatured(vendor)"
                    class="p-2 text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                    :title="vendor.is_featured ? $t('superadmin.vendors.unfeature') : $t('superadmin.vendors.feature')"
                  >
                    <component :is="vendor.is_featured ? HeartOff : Star" class="w-5 h-5" />
                  </button>
                  <NuxtLink 
                    :to="`/superadmin/vendors/${vendor.id}`"
                    class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    :title="$t('superadmin.vendors.view')"
                  >
                    <Eye class="w-5 h-5" />
                  </NuxtLink>
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
            :class="['px-3 py-1.5 text-sm rounded-lg transition-colors', p === page ? 'bg-teal-600 text-white' : 'border border-gray-200 hover:bg-gray-50']"
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
      <div v-if="loading" class="flex items-center justify-center py-12">
        <Loader2 class="w-8 h-8 animate-spin text-slate-600" />
      </div>
      
      <!-- Empty State -->
      <div v-else-if="vendors.length === 0" class="flex flex-col items-center justify-center py-12 text-center">
        <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
          <Store class="w-8 h-8 text-gray-400" />
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-1">{{ $t('superadmin.vendors.noVendors') }}</h3>
        <p class="text-gray-500 text-sm">{{ $t('superadmin.vendors.noVendorsDescription') }}</p>
      </div>
    </div>

    <!-- Analytics Modal -->
    <UiModal v-if="showAnalytics" :model-value="showAnalytics" title="Analytics de Vendors" max-width="max-w-5xl" @update:model-value="showAnalytics = false">
      <div class="space-y-6">
          <!-- Summary Cards -->
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="bg-slate-50 rounded-xl p-4">
              <p class="text-sm text-gray-500">Total Vendors</p>
              <p class="text-2xl font-bold">{{ analytics.total_vendors }}</p>
            </div>
            <div class="bg-green-50 rounded-xl p-4">
              <p class="text-sm text-gray-500">Activos</p>
              <p class="text-2xl font-bold text-green-600">{{ analytics.active_vendors }}</p>
            </div>
            <div class="bg-amber-50 rounded-xl p-4">
              <p class="text-sm text-gray-500">Pendientes</p>
              <p class="text-2xl font-bold text-amber-600">{{ analytics.pending_approval }}</p>
            </div>
            <div class="bg-red-50 rounded-xl p-4">
              <p class="text-sm text-gray-500">Suspendidos</p>
              <p class="text-2xl font-bold text-red-600">{{ analytics.suspended_vendors }}</p>
            </div>
          </div>

          <!-- Top Performers -->
          <div v-if="analytics.top_performers?.length > 0">
            <h3 class="font-bold text-gray-900 mb-4">Top Performers</h3>
            <div class="space-y-3">
              <div 
                v-for="(vendor, index) in analytics.top_performers.slice(0, 5)" 
                :key="vendor.vendor_id"
                class="flex items-center gap-4 p-4 bg-gray-50 rounded-xl"
              >
                <div 
                  class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold"
                  :class="index === 0 ? 'bg-yellow-400 text-black' : index === 1 ? 'bg-gray-300 text-black' : index === 2 ? 'bg-amber-600 text-white' : 'bg-gray-200 text-gray-600'"
                >
                  {{ index + 1 }}
                </div>
                <div class="flex-1">
                  <p class="font-medium">{{ vendor.vendor_id }}</p>
                  <p class="text-sm text-gray-500">{{ vendor.total_bookings }} reservas</p>
                </div>
                <div class="text-right">
                  <p class="font-bold text-green-600">${{ formatNumber(vendor.total_revenue) }}</p>
                  <p class="text-sm text-yellow-600 flex items-center gap-1">
            <Star class="w-3 h-3 fill-yellow-400 text-yellow-400" />
            {{ vendor.average_rating.toFixed(1) }}
          </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Registrations -->
          <div v-if="analytics.recent_registrations?.length > 0">
            <h3 class="font-bold text-gray-900 mb-4">Registros Recientes</h3>
            <div class="space-y-2">
              <div 
                v-for="vendor in analytics.recent_registrations" 
                :key="vendor.id"
                class="flex justify-between items-center p-3 border border-gray-200 rounded-lg"
              >
                <div>
                  <p class="font-medium">{{ vendor.business_name }}</p>
                  <p class="text-sm text-gray-500">{{ vendor.owner_name }}</p>
                </div>
                <UiBadge :variant="statusVariant(vendor.status)">
                  {{ formatStatus(vendor.status) }}
                </UiBadge>
              </div>
            </div>
          </div>
        </div>
    </UiModal>

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
import { Search, Filter, Download, Plus, MoreVertical, Edit, Trash2, Eye, CheckCircle, XCircle, Star, Store, MapPin, Phone, Mail, Calendar, TrendingUp, Users, DollarSign, Package, BarChart3, HeartOff, Clock, X, Loader2 } from 'lucide-vue-next'

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
      page: page.value,
      page_size: pageSize.value,
    }
    if (filters.value.status !== 'all') params.status = filters.value.status
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.type) params.business_type = filters.value.type
    if (filters.value.featured_only) params.featured_only = 'true'
    
    const response = await api.get('/superadmin/vendors', params)
    vendors.value = response.items || response
    total.value = response.total || vendors.value.length
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
    const response = await api.get('/superadmin/vendors/analytics/overview?days=30')
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

const formatNumber = (num: number) => {
  if (!num) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

watch(showAnalytics, (show) => {
  if (show) loadStats()
})

onMounted(() => {
  loadVendors()
  loadStats()
})
</script>

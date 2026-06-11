<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">{{ $t('superadmin.users.title') }}</h1>
        <p class="text-gray-500 mt-1">{{ $t('superadmin.users.subtitle') }}</p>
      </div>
      <NuxtLink 
        to="/superadmin/users/create" 
        class="px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors flex items-center gap-2"
      >
        <Plus class="w-4 h-4" />
        <span>{{ $t('superadmin.users.newUser') }}</span>
      </NuxtLink>
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
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-transparent"
              @input="debouncedSearch"
            >
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Rol</label>
          <UiSelect v-model="filters.role" :options="roleOptions" placeholder="Todos los roles" @update:model-value="loadUsers" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
          <UiSelect v-model="filters.is_active" :options="activeOptions" placeholder="Todos" @update:model-value="loadUsers" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Verificado</label>
          <UiSelect v-model="filters.is_verified" :options="verifiedOptions" placeholder="Todos" @update:model-value="loadUsers" />
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usuario</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rol</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Último acceso</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actividad</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 font-bold text-sm">
                    {{ getInitials(user.full_name) }}
                  </div>
                  <div class="ml-3">
                    <div class="text-sm font-medium text-gray-900">{{ user.full_name }}</div>
                    <div class="text-sm text-gray-500">{{ user.email }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2 py-1 text-xs font-semibold rounded-full"
                  :class="getRoleBadgeClass(user.role)"
                >
                  {{ formatRole(user.role) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2 py-1 text-xs font-semibold rounded-full"
                  :class="user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                >
                  {{ user.is_active ? $t('superadmin.users.status.active') : $t('superadmin.users.status.inactive') }}
                </span>
                <span 
                  v-if="!user.is_verified"
                  class="ml-1 px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800"
                >
                  {{ $t('superadmin.users.status.unverified') }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ user.last_login ? formatTimeAgo(user.last_login) : $t('superadmin.users.never') }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div class="flex gap-2">
                  <span v-if="user.booking_count > 0" class="text-blue-600">
                    {{ user.booking_count }} reservas
                  </span>
                  <span v-if="user.vendor_count > 0" class="text-purple-600">
                    {{ user.vendor_count }} vendor
                  </span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button 
                    @click="confirmImpersonateUser(user)"
                    class="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
                    :title="$t('superadmin.users.impersonate')"
                  >
                    <UserCircle class="w-5 h-5" />
                  </button>
                  <NuxtLink 
                    :to="`/superadmin/users/${user.id}`"
                    class="p-2 text-blue-600 hover:text-blue-900 hover:bg-blue-50 rounded-lg transition-colors"
                    :title="$t('superadmin.users.view')"
                  >
                    <Eye class="w-5 h-5" />
                  </NuxtLink>
                  <button 
                    @click="confirmToggleUserStatus(user)"
                    class="p-2 rounded-lg transition-colors"
                    :class="user.is_active ? 'text-red-600 hover:text-red-900 hover:bg-red-50' : 'text-green-600 hover:text-green-900 hover:bg-green-50'"
                    :title="user.is_active ? $t('superadmin.users.block') : $t('superadmin.users.activate')"
                  >
                    <component :is="user.is_active ? Lock : LockOpen" class="w-5 h-5" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-12">
        <Loader2 class="w-8 h-8 animate-spin text-slate-600" />
      </div>
      
      <!-- Empty State -->
      <div v-else-if="users.length === 0" class="flex flex-col items-center justify-center py-12 text-center">
        <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
          <UserCircle class="w-8 h-8 text-gray-400" />
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-1">{{ $t('superadmin.users.noUsers') }}</h3>
        <p class="text-gray-500 text-sm">{{ $t('superadmin.users.noUsersDescription') }}</p>
      </div>

      <!-- Pagination -->
      <div v-else class="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
        <div class="text-sm text-gray-500">
          {{ $t('superadmin.users.showing', { count: users.length, total: totalCount }) }}
        </div>
        <div class="flex gap-2">
          <button 
            @click="currentPage--"
            :disabled="currentPage === 1"
            class="px-3 py-1 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            ← {{ $t('common.prev') }}
          </button>
          <span class="px-3 py-1 text-sm text-gray-600">
            {{ $t('superadmin.users.page', { page: currentPage }) }}
          </span>
          <button 
            @click="currentPage++"
            :disabled="users.length < pageSize"
            class="px-3 py-1 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            {{ $t('common.next') }} →
          </button>
        </div>
      </div>
    </div>

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
import { Search, Filter, Download, Plus, MoreVertical, Edit, Trash2, Eye, CheckCircle, XCircle, Loader2, UserCircle, Lock, LockOpen } from 'lucide-vue-next'

definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()

const users = ref<any[]>([])
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = 20
const loading = ref(false)

const showConfirm = ref(false)
const confirmTitle = ref('')
const confirmMessage = ref('')
const confirmConfirmText = ref('Confirmar')
const confirmVariant = ref<'danger' | 'warning' | 'info'>('danger')
const confirmLoading = ref(false)
let confirmAction: (() => Promise<void>) | null = null

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

const toast = useToast()

const roleOptions = [
  { value: 'super_admin', label: 'Super Admin' },
  { value: 'admin', label: 'Admin' },
  { value: 'agent', label: 'Agent' },
  { value: 'customer_service', label: 'Customer Service' },
  { value: 'vendor', label: 'Vendor' },
  { value: 'client', label: 'Client' },
]

const activeOptions = [
  { value: 'true', label: 'Activos' },
  { value: 'false', label: 'Inactivos' },
]

const verifiedOptions = [
  { value: 'true', label: 'Verificados' },
  { value: 'false', label: 'Sin verificar' },
]

const filters = ref({
  search: '',
  role: '',
  is_active: '',
  is_verified: '',
})

let searchTimeout: NodeJS.Timeout

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadUsers()
  }, 300)
}

const loadUsers = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      limit: pageSize.toString(),
      offset: ((currentPage.value - 1) * pageSize).toString(),
    })
    
    if (filters.value.search) params.append('search', filters.value.search)
    if (filters.value.role) params.append('role', filters.value.role)
    if (filters.value.is_active) params.append('is_active', filters.value.is_active)
    if (filters.value.is_verified) params.append('is_verified', filters.value.is_verified)

    const response = await api.get(`/superadmin/users?${params}`)
    users.value = response

    // Load count
    const countResponse = await api.get(`/superadmin/users/count?${params}`)
    totalCount.value = countResponse.count
  } catch (error) {
    console.error('Error loading users:', error)
  } finally {
    loading.value = false
  }
}

const getInitials = (name: string) => {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

const formatRole = (role: string) => {
  const roles: Record<string, string> = {
    super_admin: 'Super Admin',
    admin: 'Admin',
    agent: 'Agent',
    customer_service: 'Customer Service',
    vendor: 'Vendor',
    client: 'Client',
  }
  return roles[role] || role
}

const getRoleBadgeClass = (role: string) => {
  const classes: Record<string, string> = {
    super_admin: 'bg-amber-100 text-amber-800',
    admin: 'bg-purple-100 text-purple-800',
    agent: 'bg-blue-100 text-blue-800',
    customer_service: 'bg-primary-100 text-primary-800',
    vendor: 'bg-orange-100 text-orange-800',
    client: 'bg-gray-100 text-gray-800',
  }
  return classes[role] || 'bg-gray-100 text-gray-800'
}

const formatTimeAgo = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000)
  
  if (diff < 60) return 'hace un momento'
  if (diff < 3600) return `hace ${Math.floor(diff / 60)} min`
  if (diff < 86400) return `hace ${Math.floor(diff / 3600)} h`
  return `hace ${Math.floor(diff / 86400)} d`
}

const confirmImpersonateUser = (user: any) => {
  openConfirm(
    'Impersonar Usuario',
    `¿Estás seguro de que quieres impersonar a ${user.full_name}? Esta acción se registrará en los logs.`,
    () => executeImpersonateUser(user),
    { confirmText: 'Impersonar', variant: 'warning' }
  )
}

const executeImpersonateUser = async (user: any) => {
  const response = await api.post(`/superadmin/users/${user.id}/impersonate`)
  sessionStorage.setItem('impersonation_token', response.impersonation_token)
  sessionStorage.setItem('original_user', JSON.stringify(useAuthStore().user))
  
  const auth = useAuthStore()
  auth.token = response.impersonation_token
  auth.user = response.target_user
  
  navigateTo('/dashboard')
}

const confirmToggleUserStatus = (user: any) => {
  const action = user.is_active ? 'bloquear' : 'activar'
  openConfirm(
    `${user.is_active ? 'Bloquear' : 'Activar'} Usuario`,
    `¿Estás seguro de que quieres ${action} a ${user.full_name}?`,
    () => executeToggleUserStatus(user),
    { confirmText: user.is_active ? 'Bloquear' : 'Activar', variant: user.is_active ? 'danger' : 'warning' }
  )
}

const executeToggleUserStatus = async (user: any) => {
  if (user.is_active) {
    await api.post(`/superadmin/users/${user.id}/block`, {}, { params: { reason: 'Blocked by Super Admin' } })
  } else {
    await api.post(`/superadmin/users/${user.id}/unblock`)
  }
  loadUsers()
}

watch(currentPage, () => {
  loadUsers()
})

onMounted(() => {
  loadUsers()
})
</script>

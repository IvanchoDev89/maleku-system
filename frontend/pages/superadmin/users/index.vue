<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ $t('superadmin.users.title') }}</h1>
        <p class="text-gray-500 mt-1">{{ $t('superadmin.users.subtitle') }}</p>
      </div>
      <NuxtLink
        to="/superadmin/users/create"
        class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
      >
        <Plus class="w-4 h-4" />
        <span>{{ $t('superadmin.users.newUser') }}</span>
      </NuxtLink>
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
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Rol</label>
          <UiSelect v-model="filters.role" :options="roleOptions" placeholder="Todos los roles" @update:model-value="loadUsers" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Estado</label>
          <UiSelect v-model="filters.is_active" :options="activeOptions" placeholder="Todos" @update:model-value="loadUsers" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Verificado</label>
          <UiSelect v-model="filters.is_verified" :options="verifiedOptions" placeholder="Todos" @update:model-value="loadUsers" />
        </div>
      </div>
    </UiCard>

    <!-- Users Table -->
    <UiTable
      :columns="columns"
      :rows="users"
      :loading="loading"
      empty-title="No hay usuarios"
      :empty-description="$t('superadmin.users.noUsersDescription')"
    >
      <template #cell-user="{ row }">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center text-primary-700 dark:text-primary-300 font-bold text-sm shrink-0">
            {{ getInitials(row.full_name) }}
          </div>
          <div class="min-w-0">
            <div class="text-sm font-medium text-gray-900 dark:text-white">{{ row.full_name }}</div>
            <div class="text-sm text-gray-500 truncate">{{ row.email }}</div>
          </div>
        </div>
      </template>
      <template #cell-role="{ row }">
        <span class="px-2 py-1 text-xs font-semibold rounded-full" :class="getRoleBadgeClass(row.role)">
          {{ formatRole(row.role) }}
        </span>
      </template>
      <template #cell-status="{ row }">
        <div class="flex gap-1">
          <span class="px-2 py-1 text-xs font-semibold rounded-full" :class="row.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
            {{ row.is_active ? $t('superadmin.users.status.active') : $t('superadmin.users.status.inactive') }}
          </span>
          <span v-if="!row.is_verified" class="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">
            {{ $t('superadmin.users.status.unverified') }}
          </span>
        </div>
      </template>
      <template #cell-last_login="{ row }">
        <span class="text-sm text-gray-500">{{ row.last_login ? formatTimeAgo(row.last_login) : $t('superadmin.users.never') }}</span>
      </template>
      <template #cell-activity="{ row }">
        <div class="flex gap-2 text-sm">
          <span v-if="row.booking_count > 0" class="text-blue-600 font-medium">{{ row.booking_count }} reservas</span>
          <span v-if="row.vendor_count > 0" class="text-purple-600 font-medium">{{ row.vendor_count }} vendor</span>
        </div>
      </template>
      <template #cell-actions="{ row }">
        <div class="flex items-center justify-end gap-1">
          <button
            @click.stop="confirmImpersonateUser(row)"
            class="p-2 text-gray-500 hover:text-gray-900 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            :title="$t('superadmin.users.impersonate')"
          >
            <UserCircle class="w-5 h-5" />
          </button>
          <NuxtLink
            :to="`/superadmin/users/${row.id}`"
            class="p-2 text-blue-600 hover:text-blue-900 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
            :title="$t('superadmin.users.view')"
          >
            <Eye class="w-5 h-5" />
          </NuxtLink>
          <button
            @click.stop="confirmToggleUserStatus(row)"
            class="p-2 rounded-lg transition-colors"
            :class="row.is_active ? 'text-red-600 hover:text-red-900 hover:bg-red-50 dark:hover:bg-red-900/30' : 'text-green-600 hover:text-green-900 hover:bg-green-50 dark:hover:bg-green-900/30'"
            :title="row.is_active ? $t('superadmin.users.block') : $t('superadmin.users.activate')"
          >
            <component :is="row.is_active ? Lock : LockOpen" class="w-5 h-5" />
          </button>
        </div>
      </template>
      <template #footer>
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-500">
            {{ $t('superadmin.users.showing', { count: users.length, total: totalCount }) }}
          </div>
          <div class="flex gap-2 items-center">
            <button
              @click="currentPage--"
              :disabled="currentPage === 1"
              class="px-3 py-1.5 text-sm rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-gray-700 dark:text-gray-300"
            >
              ← {{ $t('common.prev') }}
            </button>
            <span class="text-sm text-gray-600 dark:text-gray-400">{{ $t('superadmin.users.page', { page: currentPage }) }}</span>
            <button
              @click="currentPage++"
              :disabled="users.length < pageSize"
              class="px-3 py-1.5 text-sm rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-gray-700 dark:text-gray-300"
            >
              {{ $t('common.next') }} →
            </button>
          </div>
        </div>
      </template>
    </UiTable>

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
import { Search, Plus, Eye, UserCircle, Lock, LockOpen } from 'lucide-vue-next'

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

const columns = [
  { key: 'user', label: 'Usuario', sortable: true },
  { key: 'role', label: 'Rol', align: 'center' as const, width: '120px' },
  { key: 'status', label: 'Estado', align: 'center' as const, width: '140px' },
  { key: 'last_login', label: 'Último acceso', hiddenOnMobile: true },
  { key: 'activity', label: 'Actividad', hiddenOnMobile: true },
  { key: 'actions', label: 'Acciones', align: 'right' as const },
]

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
onUnmounted(() => clearTimeout(searchTimeout))

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
    super_admin: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-300',
    admin: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
    agent: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
    customer_service: 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-300',
    vendor: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300',
    client: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
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
  try {
    const response = await api.post(`/superadmin/users/${user.id}/impersonate`)
    const auth = useAuthStore()
    auth.token = response.impersonation_token
    auth.user = response.target_user
    navigateTo('/')
  } catch (error: any) {
    toast.error(error?.data?.detail || error?.message || 'Error al impersonar usuario')
  }
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
    await api.post(`/superadmin/users/${user.id}/block`, { reason: 'Blocked by Super Admin' })
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

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Gestión de Administradores</h1>
        <p class="text-gray-500 mt-1">Matriz de permisos y roles del sistema</p>
      </div>
      <div class="flex gap-3">
        <button
          @click="showPermissionMatrix = true"
          class="px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors flex items-center gap-2"
        >
          <span>🔐</span>
          <span>Matriz de Permisos</span>
        </button>
        <NuxtLink
          to="/superadmin/users/create"
          class="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors flex items-center gap-2"
        >
          <span>+</span>
          <span>Nuevo Admin</span>
        </NuxtLink>
      </div>
    </div>

    <!-- Role Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="role in roleSummaries"
        :key="role.role"
        class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow cursor-pointer"
        @click="selectedRole = role.role; showPermissionMatrix = true"
      >
        <div class="flex items-start justify-between">
          <div>
            <h3 class="font-bold text-gray-900">{{ role.display_name }}</h3>
            <p class="text-sm text-gray-500 mt-1">{{ role.user_count }} usuarios activos</p>
          </div>
          <UiBadge :variant="roleVariant(role.role)">
            {{ role.role }}
          </UiBadge>
        </div>

        <div class="mt-4">
          <p class="text-xs text-gray-500 uppercase tracking-wider mb-2">Módulos</p>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="module in role.modules.slice(0, 5)"
              :key="module"
              class="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs"
            >
              {{ module }}
            </span>
            <span v-if="role.modules.length > 5" class="text-xs text-gray-400">
              +{{ role.modules.length - 5 }} más
            </span>
          </div>
          <p v-if="role.modules.length === 0" class="text-xs text-gray-400 italic">
            Sin permisos configurados
          </p>
        </div>

        <div class="mt-4 pt-4 border-t border-gray-100 flex justify-between items-center">
          <span class="text-xs text-gray-500">
            {{ role.is_system_role ? 'Rol del Sistema' : 'Rol Personalizado' }}
          </span>
          <button class="text-amber-600 text-sm hover:underline">
            Configurar →
          </button>
        </div>
      </div>
    </div>

    <!-- Admin Users List -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-6 border-b border-gray-200">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-bold text-gray-900">Usuarios Administrativos</h3>
          <div class="flex gap-2">
            <UiSelect v-model="adminFilterRole" :options="roleOptions" placeholder="Todos los roles" @update:model-value="loadAdminUsers" />
          </div>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usuario</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rol</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Último Acceso</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">2FA</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="user in adminUsers" :key="user.id" class="hover:bg-gray-50">
              <td class="px-6 py-4">
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
              <td class="px-6 py-4">
                <UiBadge :variant="roleVariant(user.role)">
                  {{ formatRole(user.role) }}
                </UiBadge>
              </td>
              <td class="px-6 py-4 text-sm text-gray-500">
                {{ user.last_login ? formatTimeAgo(user.last_login) : 'Nunca' }}
              </td>
              <td class="px-6 py-4">
                <UiBadge :variant="user.has_2fa ? 'success' : 'default'">
                  {{ user.has_2fa ? 'Activado' : 'No activado' }}
                </UiBadge>
              </td>
              <td class="px-6 py-4 text-right">
                <div class="flex items-center justify-end gap-2">
                  <button
                    @click="confirmImpersonateUser(user)"
                    class="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg"
                    title="Impersonar"
                  >
                    👤
                  </button>
                  <NuxtLink
                    :to="`/superadmin/users/${user.id}`"
                    class="p-2 text-blue-600 hover:text-blue-900 hover:bg-blue-50 rounded-lg"
                  >
                    👁️
                  </NuxtLink>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Permission Matrix Modal -->
    <UiModal v-model="showPermissionMatrix" title="Matriz de Permisos" max-width="max-w-6xl">
      <p class="text-gray-500 text-sm mb-4">Configura permisos granulares por rol y módulo</p>
      <div class="mb-6">
        <UiSelect v-model="selectedRole" :options="modalRoleOptions" placeholder="Seleccionar rol" @update:model-value="loadRolePermissions" />
      </div>
      <div v-if="loadingPermissions" class="flex justify-center py-12">
        <span class="text-gray-500">Cargando permisos...</span>
      </div>

      <div v-else class="space-y-6">
        <div
          v-for="module in permissionMatrix"
          :key="module.module"
          class="border border-gray-200 rounded-xl overflow-hidden"
        >
          <!-- Module Header -->
          <div
            class="px-4 py-3 bg-gray-50 border-b border-gray-200 flex justify-between items-center cursor-pointer"
            @click="toggleModule(module.module)"
          >
            <div class="flex items-center gap-3">
              <span class="text-lg">{{ getModuleIcon(module.module) }}</span>
              <span class="font-semibold text-gray-900 capitalize">{{ module.module }}</span>
              <span
                class="px-2 py-0.5 text-xs rounded-full"
                :class="getModulePermissionCount(module.module) > 0 ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'"
              >
                {{ getModulePermissionCount(module.module) }} permisos
              </span>
            </div>
            <span class="text-gray-400">
              {{ expandedModules.includes(module.module) ? '▼' : '▶' }}
            </span>
          </div>

          <!-- Module Permissions -->
          <div v-show="expandedModules.includes(module.module)" class="p-4">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div
                v-for="perm in module.permissions"
                :key="perm.action"
                class="flex items-start gap-3 p-3 rounded-lg border transition-all"
                :class="isPermissionGranted(module.module, perm.action)
                  ? 'bg-green-50 border-green-200'
                  : 'bg-gray-50 border-gray-200 hover:border-gray-300'"
              >
                <input
                  type="checkbox"
                  :checked="isPermissionGranted(module.module, perm.action)"
                  @change="togglePermission(module.module, perm.action, $event.target.checked)"
                  class="mt-1 w-4 h-4 text-slate-900 rounded border-gray-300 focus:ring-slate-500"
                >
                <div class="flex-1">
                  <p class="font-medium text-sm text-gray-900 capitalize">{{ perm.action }}</p>
                  <p class="text-xs text-gray-500">{{ perm.description }}</p>
                  <div class="flex gap-2 mt-2">
                    <span class="px-1.5 py-0.5 bg-gray-200 text-gray-600 text-xs rounded">
                      {{ perm.scope }}
                    </span>
                    <span v-if="perm.requires_2fa" class="px-1.5 py-0.5 bg-amber-100 text-amber-700 text-xs rounded">
     2FA
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="text-sm text-gray-500">
          <span v-if="hasChanges" class="text-amber-600 font-medium">⚠️ Hay cambios sin guardar</span>
          <span v-else>Sin cambios pendientes</span>
        </div>
        <div class="flex gap-3">
          <button
            @click="confirmResetDefaults"
            class="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            :disabled="!selectedRole"
          >
            Restablecer
          </button>
          <button
            @click="savePermissions"
            class="px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors"
            :disabled="!hasChanges || saving"
          >
            {{ saving ? 'Guardando...' : 'Guardar Cambios' }}
          </button>
        </div>
      </template>
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
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()

// State
const roleSummaries = ref<any[]>([])
const adminUsers = ref<any[]>([])
const adminFilterRole = ref('')
const showPermissionMatrix = ref(false)
const selectedRole = ref('admin')
const permissionMatrix = ref<any[]>([])
const rolePermissions = ref<Record<string, any>>({})
const expandedModules = ref<string[]>(['users', 'vendors'])
const loadingPermissions = ref(false)
const hasChanges = ref(false)
const saving = ref(false)
const pendingChanges = ref<Record<string, string[]>>({})

const showConfirm = ref(false)
const confirmTitle = ref('')
const confirmMessage = ref('')
const confirmConfirmText = ref('Confirmar')
const confirmVariant = ref<'danger' | 'warning' | 'info'>('danger')
const confirmLoading = ref(false)
let confirmAction: (() => Promise<void>) | null = null

const roleOptions = [
  { value: '', label: 'Todos los roles' },
  { value: 'super_admin', label: 'Super Admin' },
  { value: 'admin', label: 'Admin' },
  { value: 'agent', label: 'Agent' },
  { value: 'customer_service', label: 'Customer Service' },
]

const modalRoleOptions = [
  { value: 'super_admin', label: 'Super Admin' },
  { value: 'admin', label: 'Admin' },
  { value: 'agent', label: 'Agent' },
  { value: 'customer_service', label: 'Customer Service' },
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

// Load data
const loadRoleSummaries = async () => {
  try {
    roleSummaries.value = await api.get('/superadmin/permissions/roles')
  } catch (error) {
    console.error('Error loading role summaries:', error)
  }
}

const loadAdminUsers = async () => {
  try {
    const params = new URLSearchParams()
    if (adminFilterRole.value) {
      params.append('role', adminFilterRole.value)
    } else {
      // Load all admin roles
      params.append('role', 'super_admin')
    }
    params.append('limit', '100')

    const response = await api.get(`/superadmin/users?${params}`)
    adminUsers.value = response
  } catch (error) {
    console.error('Error loading admin users:', error)
  }
}

const loadPermissionMatrix = async () => {
  try {
    permissionMatrix.value = await api.get('/superadmin/permissions/matrix')
  } catch (error) {
    console.error('Error loading permission matrix:', error)
  }
}

const loadRolePermissions = async () => {
  if (!selectedRole.value) return

  loadingPermissions.value = true
  try {
    const response = await api.get(`/superadmin/permissions/roles/${selectedRole.value}`)
    rolePermissions.value = {}
    pendingChanges.value = {}
    hasChanges.value = false

    // Organize by module
    for (const perm of response) {
      rolePermissions.value[perm.module] = perm.permissions
    }
  } catch (error) {
    console.error('Error loading role permissions:', error)
  } finally {
    loadingPermissions.value = false
  }
}

// Helpers
const getInitials = (name: string) => {
  if (!name) return '?'
  return name.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2)
}

const formatRole = (role: string) => {
  const roles: Record<string, string> = {
    super_admin: 'Super Admin',
    admin: 'Administrador',
    agent: 'Agente',
    customer_service: 'Customer Service',
    vendor: 'Vendor',
    client: 'Cliente',
  }
  return roles[role] || role
}

function roleVariant(role: string) {
  const map: Record<string, string> = {
    super_admin: 'info',
    admin: 'warning',
    agent: 'default',
    customer_service: 'success',
    vendor: 'warning',
    client: 'default',
  }
  return (map[role] || 'default') as any
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

const getModuleIcon = (module: string) => {
  const icons: Record<string, string> = {
    users: '👥',
    vendors: '🏪',
    properties: '🏨',
    bookings: '📋',
    content: '📝',
    analytics: '📊',
    system: '⚙️',
  }
  return icons[module] || '📦'
}

const toggleModule = (module: string) => {
  if (expandedModules.value.includes(module)) {
    expandedModules.value = expandedModules.value.filter(m => m !== module)
  } else {
    expandedModules.value.push(module)
  }
}

const isPermissionGranted = (module: string, action: string) => {
  // Check pending changes first
  if (pendingChanges.value[module]) {
    return pendingChanges.value[module].includes(action)
  }
  // Fall back to saved permissions
  return rolePermissions.value[module]?.includes(action) || false
}

const getModulePermissionCount = (module: string) => {
  if (pendingChanges.value[module]) {
    return pendingChanges.value[module].length
  }
  return rolePermissions.value[module]?.length || 0
}

const togglePermission = (module: string, action: string, granted: boolean) => {
  if (!pendingChanges.value[module]) {
    // Initialize with current permissions
    pendingChanges.value[module] = [...(rolePermissions.value[module] || [])]
  }

  if (granted) {
    if (!pendingChanges.value[module].includes(action)) {
      pendingChanges.value[module].push(action)
    }
  } else {
    pendingChanges.value[module] = pendingChanges.value[module].filter((a: string) => a !== action)
  }

  hasChanges.value = Object.keys(pendingChanges.value).length > 0
}

const savePermissions = async () => {
  saving.value = true
  try {
    for (const [module, permissions] of Object.entries(pendingChanges.value)) {
      await api.post(`/superadmin/permissions/roles/${selectedRole.value}/modules/${module}`, {
        role: selectedRole.value,
        module,
        permissions,
        is_active: true,
      })
    }

    // Clear pending changes
    pendingChanges.value = {}
    hasChanges.value = false

    // Reload
    await loadRolePermissions()
    await loadRoleSummaries()
  } catch (error) {
    console.error('Error saving permissions:', error)
  } finally {
    saving.value = false
  }
}

const confirmResetDefaults = () => {
  openConfirm(
    'Restablecer Permisos',
    `¿Estás seguro de restablecer todos los permisos de ${formatRole(selectedRole.value)} a los valores por defecto?`,
    executeResetDefaults,
    { confirmText: 'Restablecer', variant: 'danger' }
  )
}

const executeResetDefaults = async () => {
  try {
    await api.post(`/superadmin/permissions/roles/${selectedRole.value}/reset`)
    await loadRolePermissions()
    await loadRoleSummaries()
  } catch (error) {
    console.error('Error resetting permissions:', error)
  }
}

const confirmImpersonateUser = (user: any) => {
  openConfirm(
    'Impersonar Usuario',
    `¿Impersonar a ${user.full_name}?`,
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
  } catch (error) {
    console.error('Error impersonating:', error)
  }
}

// Watchers
watch(showPermissionMatrix, (show) => {
  if (show) {
    loadPermissionMatrix()
    loadRolePermissions()
  }
})

// Init
onMounted(() => {
  loadRoleSummaries()
  loadAdminUsers()
})
</script>

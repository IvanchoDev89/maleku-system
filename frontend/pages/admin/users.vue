<template>
  <div>
    <div v-if="error" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
      {{ error }}
      <button @click="loadUsers" class="ml-3 underline hover:no-underline">Reintentar</button>
    </div>

    <div class="flex justify-between items-center mb-6">
      <div class="flex gap-4">
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar usuarios..."
            class="pl-11 pr-4 py-2.5 bg-white text-gray-700 rounded-xl border border-gray-200 shadow-sm focus:border-primary focus:ring-2 focus:ring-primary/20 w-64"
            @input="debouncedSearch"
          />
          <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <UiSelect v-model="roleFilter" :options="roleOptions" placeholder="Todos los roles" @update:model-value="debouncedSearch" />
      </div>
      <button
        @click="openCreateModal"
        class="bg-primary hover:bg-primary-700 text-white px-5 py-2.5 rounded-xl font-medium shadow-md hover:shadow-lg transition-all"
      >
        + Nuevo Usuario
      </button>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="text-left p-4 text-gray-500 font-semibold text-sm">Usuario</th>
              <th class="text-left p-4 text-gray-500 font-semibold text-sm">Rol</th>
              <th class="text-left p-4 text-gray-500 font-semibold text-sm">Estado</th>
              <th class="text-left p-4 text-gray-500 font-semibold text-sm">Verificado</th>
              <th class="text-left p-4 text-gray-500 font-semibold text-sm">Registrado</th>
              <th class="text-left p-4 text-gray-500 font-semibold text-sm">Acciones</th>
            </tr>
          </thead>
          <tbody v-if="loading">
            <tr v-for="i in 5" :key="i" class="border-t border-gray-100">
              <td colspan="6" class="p-4">
                <div class="flex gap-4 animate-pulse">
                  <div class="w-10 h-10 bg-gray-200 rounded-full shrink-0" />
                  <div class="flex-1 space-y-2">
                    <div class="h-4 bg-gray-200 rounded w-40" />
                    <div class="h-3 bg-gray-200 rounded w-60" />
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
          <tbody v-else>
            <tr v-for="user in users" :key="user.id" class="border-t border-gray-100 hover:bg-gray-50/50 transition-colors">
              <td class="p-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center text-primary font-bold shrink-0">
                    {{ user.full_name.charAt(0).toUpperCase() }}
                  </div>
                  <div class="min-w-0">
                    <p class="text-gray-900 font-medium truncate">{{ user.full_name }}</p>
                    <p class="text-gray-500 text-sm truncate">{{ user.email }}</p>
                  </div>
                </div>
              </td>
              <td class="p-4">
                <UiBadge :variant="roleBadgeVariant(user.role)" size="sm">
                  {{ getRoleLabel(user.role) }}
                </UiBadge>
              </td>
              <td class="p-4">
                <button @click="toggleUserStatus(user)" class="flex items-center gap-2">
                  <span class="w-2.5 h-2.5 rounded-full" :class="user.is_active ? 'bg-green-500' : 'bg-red-400'" />
                  <span class="text-gray-700">{{ user.is_active ? 'Activo' : 'Inactivo' }}</span>
                </button>
              </td>
              <td class="p-4">
                <span v-if="user.is_verified" class="text-green-600 font-medium">✓ Verificado</span>
                <span v-else class="text-gray-400">Pendiente</span>
              </td>
              <td class="p-4 text-gray-500 text-sm whitespace-nowrap">
                {{ formatDate(user.created_at) }}
              </td>
              <td class="p-4">
                <div class="flex gap-2">
                  <button @click="editUser(user)" class="p-2 text-gray-400 hover:text-primary hover:bg-primary/5 rounded-lg transition-colors" title="Editar">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button @click="openDeleteDialog(user)" class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors" title="Eliminar">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v4m0-4h4m-2 0v2m-2-4h4m4-4h-4m0 4v4m0-4h-4m0 4v-4m0-4h4" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="users.length === 0 && !loading" class="p-8 text-center text-gray-400">
        No hay usuarios registrados
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="total > pageSize" class="flex items-center justify-between mt-4">
      <p class="text-sm text-gray-500">
        Mostrando {{ (page - 1) * pageSize + 1 }}-{{ Math.min(page * pageSize, total) }} de {{ total }}
      </p>
      <div class="flex gap-1">
        <button :disabled="page <= 1" class="px-3 py-1.5 text-sm rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors" @click="changePage(page - 1)">Anterior</button>
        <button v-for="p in totalPages" :key="p" :class="['px-3 py-1.5 text-sm rounded-lg transition-colors', p === page ? 'bg-primary-600 text-white' : 'border border-gray-200 hover:bg-gray-50']" @click="changePage(p)">{{ p }}</button>
        <button :disabled="page >= totalPages" class="px-3 py-1.5 text-sm rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors" @click="changePage(page + 1)">Siguiente</button>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <UiModal :model-value="showModal" :title="editingUser ? 'Editar Usuario' : 'Nuevo Usuario'" max-width="max-w-lg" @update:model-value="closeModal">
      <form @submit.prevent="saveUser" class="space-y-4">
        <div>
          <label class="block text-gray-500 text-sm mb-1.5">Nombre completo</label>
          <input v-model="form.full_name" type="text" required class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
        </div>
        <div>
          <label class="block text-gray-500 text-sm mb-1.5">Email</label>
          <input v-model="form.email" type="email" required class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
        </div>
        <div>
          <label class="block text-gray-500 text-sm mb-1.5">Teléfono</label>
          <input v-model="form.phone" type="tel" class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
        </div>
        <div v-if="!editingUser">
          <label class="block text-gray-500 text-sm mb-1.5">Contraseña</label>
          <input v-model="form.password" type="password" required class="w-full bg-gray-50 text-gray-700 px-4 py-2.5 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20" />
        </div>
        <div>
          <label class="block text-gray-500 text-sm mb-1.5">Rol</label>
          <UiSelect v-model="form.role" :options="roleSelectOptions" />
        </div>
      </form>
      <template #footer>
        <button type="button" @click="closeModal" class="px-4 py-2.5 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors">Cancelar</button>
        <button type="submit" @click="saveUser" :disabled="saving" class="px-4 py-2.5 bg-primary text-white rounded-xl hover:bg-primary-700 disabled:opacity-50 transition-colors">
          {{ saving ? 'Guardando...' : editingUser ? 'Actualizar' : 'Crear' }}
        </button>
      </template>
    </UiModal>

    <!-- Delete Confirmation -->
    <UiConfirmDialog
      :model-value="!!userToDelete"
      title="Eliminar Usuario"
      :message="`¿Estás seguro de eliminar a ${userToDelete?.full_name}? Esta acción no se puede deshacer.`"
      confirm-text="Eliminar"
      variant="danger"
      :loading="deleting"
      @update:model-value="userToDelete = null"
      @confirm="confirmDelete"
    />
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['auth']
})

const api = useApi()
const auth = useAuthStore()
const toast = useToast()

interface User {
  id: string
  email: string
  full_name: string
  phone?: string
  role: string
  is_active: boolean
  is_verified: boolean
  created_at: string
}

const users = ref<User[]>([])
const loading = ref(false)
const error = ref('')
const searchQuery = ref('')
const roleFilter = ref('')
const showModal = ref(false)
const editingUser = ref<User | null>(null)
const saving = ref(false)
const userToDelete = ref<User | null>(null)
const deleting = ref(false)

const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

const roleOptions = [
  { value: '', label: 'Todos los roles' },
  { value: 'client', label: 'Cliente' },
  { value: 'vendor', label: 'Proveedor' },
  { value: 'agent', label: 'Agente' },
  { value: 'customer_service', label: 'Soporte' },
  { value: 'admin', label: 'Admin' },
  { value: 'super_admin', label: 'Super Admin' }
]

const roleSelectOptions = [
  { value: 'client', label: 'Cliente' },
  { value: 'vendor', label: 'Proveedor' },
  { value: 'agent', label: 'Agente' },
  { value: 'customer_service', label: 'Soporte' },
  { value: 'admin', label: 'Admin' }
]

const form = reactive({
  full_name: '',
  email: '',
  phone: '',
  password: '',
  role: 'client' as string
})

function roleBadgeVariant(role: string) {
  const map: Record<string, string> = {
    super_admin: 'danger',
    admin: 'warning',
    agent: 'info',
    customer_service: 'info',
    vendor: 'default',
    client: 'success'
  }
  return (map[role] || 'default') as any
}

const getRoleLabel = (role: string) => {
  const labels: Record<string, string> = {
    super_admin: 'Super Admin',
    admin: 'Admin',
    agent: 'Agente',
    customer_service: 'Soporte',
    vendor: 'Proveedor',
    client: 'Cliente'
  }
  return labels[role] || role
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('es-CR', { year: 'numeric', month: 'short', day: 'numeric' })
}

const loadUsers = async () => {
  loading.value = true
  error.value = ''
  try {
    const params: Record<string, any> = { page: page.value, page_size: pageSize.value }
    if (searchQuery.value) params.search = searchQuery.value
    if (roleFilter.value) params.role = roleFilter.value
    const data = await api.get('/users', params)
    users.value = data.items || []
    total.value = data.total || users.value.length
  } catch (e) {
    error.value = 'Error al cargar usuarios'
  } finally {
    loading.value = false
  }
}

let searchTimeout: ReturnType<typeof setTimeout>
onUnmounted(() => clearTimeout(searchTimeout))
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => { page.value = 1; loadUsers() }, 300)
}

const changePage = (p: number) => {
  page.value = p
  loadUsers()
}

const openCreateModal = () => {
  editingUser.value = null
  form.full_name = ''
  form.email = ''
  form.phone = ''
  form.password = ''
  form.role = 'client'
  showModal.value = true
}

const editUser = (user: User) => {
  editingUser.value = user
  form.full_name = user.full_name
  form.email = user.email
  form.phone = user.phone || ''
  form.role = user.role
  form.password = ''
  showModal.value = true
}

const saveUser = async () => {
  saving.value = true
  try {
    if (editingUser.value) {
      await api.put(`/users/${editingUser.value.id}`, { full_name: form.full_name, phone: form.phone, role: form.role })
    } else {
      await api.post('/auth/register', form)
    }
    closeModal()
    loadUsers()
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al guardar usuario')
  } finally {
    saving.value = false
  }
}

const closeModal = () => {
  showModal.value = false
  editingUser.value = null
}

const openDeleteDialog = (user: User) => {
  userToDelete.value = user
}

const confirmDelete = async () => {
  if (!userToDelete.value) return
  deleting.value = true
  try {
    await api.delete(`/users/${userToDelete.value.id}`)
    userToDelete.value = null
    loadUsers()
  } catch (e) {
    console.error('Error deleting user:', e)
  } finally {
    deleting.value = false
  }
}

const toggleUserStatus = async (user: User) => {
  try {
    await api.patch(`/users/${user.id}`, { is_active: !user.is_active })
    loadUsers()
  } catch (e) {
    console.error('Error toggling user status:', e)
  }
}

onMounted(() => {
  auth.initAuth()
  loadUsers()
})
</script>

<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin'],
})

const route = useRoute()
const router = useRouter()
const api = useApi()
const toast = useToast()
const userId = route.params.id as string

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

const loading = ref(true)
const error = ref('')
const user = ref<any>(null)
const bookings = ref<any[]>([])
const activityLogs = ref<any[]>([])

const roleOptions = [
  { value: 'client', label: 'client' },
  { value: 'agent', label: 'agent' },
  { value: 'admin', label: 'admin' },
  { value: 'vendor', label: 'vendor' },
]

const goBack = () => router.push('/superadmin/users')

const blockUser = async () => {
  try {
    const action = user.value.is_active ? 'block' : 'unblock'
    await api.post(`/superadmin/users/${userId}/${action}`)
    user.value.is_active = !user.value.is_active
    toast.success(user.value.is_active ? 'Usuario desbloqueado' : 'Usuario bloqueado')
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al cambiar estado')
  }
}

const impersonateUser = async () => {
  try {
    await api.post(`/superadmin/users/${userId}/impersonate`)
    toast.info(`Impersonando usuario ${user.value.email}`)
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al impersonar')
  }
}

const updateRole = async (newRole: string) => {
  try {
    await api.put(`/superadmin/users/${userId}`, { role: newRole })
    user.value.role = newRole
    toast.success('Rol actualizado')
  } catch (e: any) {
    toast.error(e?.data?.detail || 'Error al actualizar rol')
  }
}

onMounted(async () => {
  if (!UUID_REGEX.test(route.params.id as string)) {
    await router.replace('/superadmin/users')
    return
  }
  loading.value = true
  try {
    const [userData, logs] = await Promise.all([
      api.get(`/superadmin/users/${userId}`),
      api.get<any[]>(`/superadmin/users/${userId}/activity`).catch((e) => { console.warn('Failed to load activity logs:', e); return [] }),
    ])
    user.value = userData
    activityLogs.value = logs
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar usuario'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div v-if="loading" class="text-center py-12">
    <p class="text-gray-500">Cargando...</p>
  </div>

  <div v-else-if="error" class="text-center py-12">
    <p class="text-red-500">{{ error }}</p>
    <button @click="goBack" class="mt-4 text-blue-600 hover:text-blue-800">← Volver</button>
  </div>

  <div v-else class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <button @click="goBack" class="p-2 hover:bg-gray-100 rounded-lg">
          <span class="text-2xl">←</span>
        </button>
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Detalle de Usuario</h1>
          <p class="text-gray-500">ID: {{ userId }}</p>
        </div>
      </div>
      <div class="flex gap-3">
        <button
          @click="impersonateUser"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          👤 Impersonar
        </button>
        <button
          @click="blockUser"
          :class="user.is_active ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'"
          class="px-4 py-2 text-white rounded-lg"
        >
          {{ user.is_active ? '🔒 Bloquear' : '🔓 Desbloquear' }}
        </button>
      </div>
    </div>

    <!-- User Profile Card -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex items-start gap-6">
        <div class="w-20 h-20 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
          {{ user.full_name?.split(' ').map((n: string) => n[0]).join('').toUpperCase() }}
        </div>
        <div class="flex-1">
          <h2 class="text-2xl font-bold text-gray-900">{{ user.full_name }}</h2>
          <p class="text-gray-500">{{ user.email }}</p>
          <div class="flex gap-3 mt-3">
            <span :class="user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="px-3 py-1 rounded-full text-sm font-medium">
              {{ user.is_active ? 'Activo' : 'Bloqueado' }}
            </span>
            <span v-if="user.is_verified" class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
              ✓ Email Verificado
            </span>
            <UiSelect v-model="user.role" :options="roleOptions" @update:model-value="updateRole" />
          </div>
        </div>
        <div class="text-right">
          <div class="text-sm text-gray-500">Registrado</div>
          <div class="font-medium">{{ user.created_at?.slice(0, 10) }}</div>
          <div class="text-sm text-gray-500 mt-2">Último login</div>
          <div class="font-medium">{{ user.last_login?.slice(0, 16) || 'Nunca' }}</div>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Teléfono</div>
        <div class="text-lg font-medium text-gray-900">{{ user.phone || 'N/A' }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Rol</div>
        <div class="text-lg font-medium text-gray-900 capitalize">{{ user.role?.replace('_', ' ') }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Intentos fallidos</div>
        <div class="text-lg font-medium text-gray-900">{{ user.failed_login_attempts || 0 }}</div>
      </div>
      <div class="bg-white rounded-lg shadow p-6">
        <div class="text-sm text-gray-500">Email verificado</div>
        <div class="text-lg font-medium" :class="user.is_verified ? 'text-green-600' : 'text-red-600'">
          {{ user.is_verified ? 'Sí' : 'No' }}
        </div>
      </div>
    </div>

    <!-- Activity Log -->
    <div class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Actividad Reciente</h3>
      <div v-if="activityLogs.length === 0" class="text-gray-400 text-sm py-4 text-center">
        No hay actividad registrada
      </div>
      <div v-else class="space-y-4">
        <div v-for="log in activityLogs.slice(0, 10)" :key="log.id" class="flex items-start gap-4 pb-4 border-b border-gray-100">
          <div class="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
            <span class="text-lg">📝</span>
          </div>
          <div class="flex-1">
            <div class="font-medium text-gray-900 capitalize">{{ log.action }}</div>
            <div class="text-sm text-gray-500">{{ log.changes_summary || log.entity_type }}</div>
          </div>
          <div class="text-right">
            <div class="text-sm text-gray-900">{{ log.created_at?.slice(0, 16) }}</div>
            <div class="text-xs text-gray-500">{{ log.ip_address }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

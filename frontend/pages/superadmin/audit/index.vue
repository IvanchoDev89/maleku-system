<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Auditoría y Logs</h1>
        <p class="text-gray-500 mt-1">Registro completo de actividad y seguridad</p>
      </div>
      <div class="flex gap-3">
        <button 
          @click="exportLogs"
          class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
        >
          <span>📥</span>
          <span>Exportar</span>
        </button>
        <button 
          @click="showFilters = !showFilters"
          class="px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors flex items-center gap-2"
        >
          <span>🔍</span>
          <span>Filtros</span>
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">Eventos Hoy</p>
        <p class="text-2xl font-bold text-gray-900">{{ stats.today_count }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">Acciones de Usuarios</p>
        <p class="text-2xl font-bold text-blue-600">{{ stats.user_actions }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">Eventos de Seguridad</p>
        <p class="text-2xl font-bold text-purple-600">{{ stats.security_events }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">Intentos Fallidos</p>
        <p class="text-2xl font-bold" :class="stats.failed_logins > 0 ? 'text-red-600' : 'text-green-600'">
          {{ stats.failed_logins }}
        </p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100">
      <div class="border-b border-gray-200">
        <div class="flex">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            @click="activeTab = tab.id"
            class="px-6 py-4 text-sm font-medium border-b-2 transition-colors"
            :class="activeTab === tab.id 
              ? 'border-slate-900 text-slate-900' 
              : 'border-transparent text-gray-500 hover:text-gray-700'"
          >
            {{ tab.label }}
            <span 
              v-if="tab.badge > 0" 
              class="ml-2 px-2 py-0.5 bg-red-100 text-red-600 rounded-full text-xs"
            >
              {{ tab.badge }}
            </span>
          </button>
        </div>
      </div>

      <!-- Filters Panel -->
      <div v-if="showFilters" class="p-4 bg-gray-50 border-b border-gray-200">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Usuario</label>
            <input 
              v-model="filters.user_email"
              type="text" 
              placeholder="Email..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Acción</label>
            <UiSelect v-model="filters.action" :options="actionOptions" placeholder="Todas" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Entidad</label>
            <UiSelect v-model="filters.entity_type" :options="entityTypeOptions" placeholder="Todas" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Fecha</label>
            <UiSelect v-model="filters.date_range" :options="dateRangeOptions" placeholder="Hoy" />
          </div>
        </div>
        <div class="mt-4 flex justify-end">
          <button 
            @click="applyFilters"
            class="px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800"
          >
            Aplicar Filtros
          </button>
        </div>
      </div>

      <!-- Audit Logs Table -->
      <div v-if="activeTab === 'audit'" class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usuario</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acción</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Entidad</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Detalles</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="log in auditLogs" :key="log.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {{ formatDateTime(log.created_at) }}
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center">
                  <div class="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 text-xs font-bold">
                    {{ getInitials(log.user_name || log.user_email) }}
                  </div>
                  <div class="ml-2">
                    <p class="text-sm font-medium text-gray-900">{{ log.user_name || 'Sistema' }}</p>
                    <p class="text-xs text-gray-500">{{ log.user_email }}</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3">
                <span 
                  class="px-2 py-1 text-xs font-semibold rounded-full"
                  :class="getActionBadgeClass(log.action)"
                >
                  {{ formatAction(log.action) }}
                </span>
              </td>
              <td class="px-4 py-3">
                <p class="text-sm text-gray-900 capitalize">{{ log.entity_type }}</p>
                <p class="text-xs text-gray-500">{{ log.entity_name || log.entity_id?.slice(0, 8) }}</p>
              </td>
              <td class="px-4 py-3">
                <p class="text-sm text-gray-600">{{ log.changes_summary || '-' }}</p>
                <button 
                  v-if="log.old_values || log.new_values"
                  @click="showLogDetails(log)"
                  class="text-xs text-blue-600 hover:underline mt-1"
                >
                  Ver cambios →
                </button>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {{ log.ip_address }}
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="auditLogs.length === 0" class="text-center py-8 text-gray-500">
          No hay registros de auditoría
        </p>
      </div>

      <!-- Security Logs Table -->
      <div v-if="activeTab === 'security'" class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usuario</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Evento</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severidad</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descripción</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP / Ubicación</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="log in securityLogs" :key="log.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {{ formatDateTime(log.created_at) }}
              </td>
              <td class="px-4 py-3">
                <p class="text-sm font-medium text-gray-900">{{ log.user_email || 'Anónimo' }}</p>
              </td>
              <td class="px-4 py-3">
                <span 
                  class="px-2 py-1 text-xs font-semibold rounded-full"
                  :class="getSecurityActionClass(log.action)"
                >
                  {{ formatSecurityAction(log.action) }}
                </span>
              </td>
              <td class="px-4 py-3">
                <span 
                  class="px-2 py-1 text-xs font-semibold rounded-full"
                  :class="getSeverityClass(log.severity)"
                >
                  {{ log.severity }}
                </span>
              </td>
              <td class="px-4 py-3">
                <p class="text-sm text-gray-600">{{ log.description }}</p>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                <p>{{ log.ip_address }}</p>
                <p v-if="log.country_code" class="text-xs">{{ log.country_code }} {{ log.city }}</p>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="securityLogs.length === 0" class="text-center py-8 text-gray-500">
          No hay eventos de seguridad
        </p>
      </div>
    </div>

    <!-- Log Details Modal -->
    <UiModal
      v-if="selectedLog"
      :model-value="true"
      title="Detalles del Log"
      max-width="max-w-3xl"
      @update:model-value="selectedLog = null"
    >
      <div class="grid grid-cols-2 gap-4 mb-6">
        <div>
          <p class="text-sm text-gray-500">Usuario</p>
          <p class="font-medium">{{ selectedLog.user_email }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Fecha</p>
          <p class="font-medium">{{ formatDateTime(selectedLog.created_at) }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Acción</p>
          <p class="font-medium">{{ selectedLog.action }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">IP</p>
          <p class="font-medium">{{ selectedLog.ip_address }}</p>
        </div>
      </div>
      
      <div v-if="selectedLog.old_values" class="mb-4">
        <p class="text-sm font-medium text-gray-700 mb-2">Valores Anteriores</p>
        <pre class="bg-gray-100 p-4 rounded-lg text-sm overflow-x-auto">{{ JSON.stringify(selectedLog.old_values, null, 2) }}</pre>
      </div>
      
      <div v-if="selectedLog.new_values" class="mb-4">
        <p class="text-sm font-medium text-gray-700 mb-2">Valores Nuevos</p>
        <pre class="bg-gray-100 p-4 rounded-lg text-sm overflow-x-auto">{{ JSON.stringify(selectedLog.new_values, null, 2) }}</pre>
      </div>
    </UiModal>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()
const toast = useToast()

const tabs = [
  { id: 'audit', label: 'Logs de Auditoría', badge: 0 },
  { id: 'security', label: 'Seguridad', badge: 0 },
]

const activeTab = ref('audit')
const showFilters = ref(false)
const auditLogs = ref<any[]>([])
const securityLogs = ref<any[]>([])
const stats = ref({
  today_count: 0,
  user_actions: 0,
  security_events: 0,
  failed_logins: 0,
})
const selectedLog = ref<any>(null)

const actionOptions = [
  { value: 'CREATE', label: 'Crear' },
  { value: 'UPDATE', label: 'Actualizar' },
  { value: 'DELETE', label: 'Eliminar' },
  { value: 'LOGIN', label: 'Iniciar Sesión' },
  { value: 'LOGOUT', label: 'Cerrar Sesión' },
  { value: 'IMPERSONATE', label: 'Impersonar' },
  { value: 'EXPORT', label: 'Exportar' },
  { value: 'APPROVE', label: 'Aprobar' },
  { value: 'REJECT', label: 'Rechazar' },
  { value: 'SUSPEND', label: 'Suspender' },
]

const entityTypeOptions = [
  { value: 'user', label: 'Usuario' },
  { value: 'vendor', label: 'Proveedor' },
  { value: 'property', label: 'Propiedad' },
  { value: 'booking', label: 'Reserva' },
  { value: 'content', label: 'Contenido' },
]

const dateRangeOptions = [
  { value: 'today', label: 'Hoy' },
  { value: 'week', label: 'Última semana' },
  { value: 'month', label: 'Último mes' },
  { value: 'custom', label: 'Personalizado' },
]

const filters = ref({
  user_email: '',
  action: '',
  entity_type: '',
  date_range: 'today',
})

const loadAuditLogs = async () => {
  try {
    const params = new URLSearchParams()
    if (filters.value.action) params.append('action', filters.value.action)
    if (filters.value.entity_type) params.append('entity_type', filters.value.entity_type)
    params.append('limit', '100')
    
    const response = await api.get(`/superadmin/audit/logs?${params}`)
    auditLogs.value = response
  } catch (error) {
    console.error('Error loading audit logs:', error)
  }
}

const loadSecurityLogs = async () => {
  try {
    const params = new URLSearchParams()
    params.append('limit', '100')
    
    const response = await api.get(`/superadmin/audit/security?${params}`)
    securityLogs.value = response
  } catch (error) {
    console.error('Error loading security logs:', error)
  }
}

const loadStats = async () => {
  try {
    const summary = await api.get('/superadmin/audit/summary')
    stats.value = summary
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

const exportLogs = async () => {
  try {
    const response = await api.post('/superadmin/audit/export', {
      format: 'csv',
      start_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      end_date: new Date().toISOString(),
    })
    
    // Download file
    const blob = new Blob([response.data], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
  } catch (error) {
    console.error('Error exporting logs:', error)
    toast.error('Error al exportar logs')
  }
}

const applyFilters = () => {
  loadAuditLogs()
  loadSecurityLogs()
  showFilters.value = false
}

const formatDateTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleString('es-CR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

const formatAction = (action: string) => {
  const actions: Record<string, string> = {
    CREATE: 'Crear',
    UPDATE: 'Actualizar',
    DELETE: 'Eliminar',
    LOGIN: 'Iniciar Sesión',
    LOGOUT: 'Cerrar Sesión',
    IMPERSONATE: 'Impersonar',
    EXPORT: 'Exportar',
    APPROVE: 'Aprobar',
    REJECT: 'Rechazar',
    SUSPEND: 'Suspender',
  }
  return actions[action] || action
}

const formatSecurityAction = (action: string) => {
  const actions: Record<string, string> = {
    LOGIN_SUCCESS: 'Login Exitoso',
    LOGIN_FAILURE: 'Login Fallido',
    PASSWORD_CHANGE: 'Cambio Contraseña',
    ACCESS_DENIED: 'Acceso Denegado',
    RATE_LIMIT_HIT: 'Límite Excedido',
    SUSPICIOUS_ACTIVITY: 'Actividad Sospechosa',
  }
  return actions[action] || action
}

const getInitials = (name: string) => {
  if (!name) return '?'
  return name.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2)
}

const getActionBadgeClass = (action: string) => {
  const classes: Record<string, string> = {
    CREATE: 'bg-green-100 text-green-800',
    UPDATE: 'bg-blue-100 text-blue-800',
    DELETE: 'bg-red-100 text-red-800',
    LOGIN: 'bg-gray-100 text-gray-800',
    LOGOUT: 'bg-gray-100 text-gray-800',
    IMPERSONATE: 'bg-purple-100 text-purple-800',
    EXPORT: 'bg-yellow-100 text-yellow-800',
  }
  return classes[action] || 'bg-gray-100 text-gray-800'
}

const getSecurityActionClass = (action: string) => {
  if (action.includes('FAILURE') || action.includes('DENIED')) {
    return 'bg-red-100 text-red-800'
  }
  if (action.includes('SUCCESS')) {
    return 'bg-green-100 text-green-800'
  }
  return 'bg-blue-100 text-blue-800'
}

const getSeverityClass = (severity: string) => {
  const classes: Record<string, string> = {
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800',
  }
  return classes[severity] || 'bg-gray-100 text-gray-800'
}

const showLogDetails = (log: any) => {
  selectedLog.value = log
}

watch(activeTab, () => {
  if (activeTab.value === 'audit') loadAuditLogs()
  if (activeTab.value === 'security') loadSecurityLogs()
})

onMounted(() => {
  loadAuditLogs()
  loadSecurityLogs()
  loadStats()
})
</script>

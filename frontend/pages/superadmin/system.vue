<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Gestión del Sistema</h1>
        <p class="text-gray-500 mt-1">Configuración, mantenimiento y monitoreo</p>
      </div>
      <div class="flex gap-3">
        <button
          v-if="maintenanceMode"
          @click="confirmToggleMaintenance"
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          <Rocket class="w-4 h-4 mr-2" /> Desactivar Mantenimiento
        </button>
        <button
          v-else
          @click="confirmToggleMaintenance"
          class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          <Wrench class="w-4 h-4 mr-2" /> Modo Mantenimiento
        </button>
      </div>
    </div>

    <!-- Maintenance Banner -->
    <div
      v-if="maintenanceMode"
      class="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center justify-between"
    >
      <div class="flex items-center gap-3">
        <AlertTriangle class="w-8 h-8 text-red-500" />
        <div>
          <p class="font-bold text-red-700">Modo Mantenimiento Activado</p>
          <p class="text-sm text-red-600">El sitio está inaccesible para usuarios públicos</p>
        </div>
      </div>
      <span class="px-3 py-1 bg-red-200 text-red-800 rounded-full text-sm font-medium">
        ACTIVO
      </span>
    </div>

    <!-- System Health Grid -->
    <template v-if="systemHealth">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- API Status -->
        <UiCard padding="md">
          <div class="flex justify-between items-start">
            <div>
              <p class="text-sm text-gray-500">API Server</p>
              <p class="text-2xl font-bold text-gray-900 mt-1">{{ systemHealth.api?.status || '—' }}</p>
            </div>
            <div
              class="w-3 h-3 rounded-full"
              :class="systemHealth.api?.status === 'healthy' ? 'bg-green-500' : 'bg-gray-300'"
            ></div>
          </div>
          <div class="mt-4 space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Versión</span>
              <span class="font-medium">{{ systemHealth.api?.version || '—' }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Tiempo activo</span>
              <span class="font-medium">{{ systemHealth.api?.uptime || '—' }}</span>
            </div>
          </div>
        </UiCard>

        <!-- Database -->
        <UiCard padding="md">
          <div class="flex justify-between items-start">
            <div>
              <p class="text-sm text-gray-500">Base de Datos</p>
              <p class="text-2xl font-bold text-gray-900 mt-1">{{ systemHealth.database?.status || '—' }}</p>
            </div>
            <div
              class="w-3 h-3 rounded-full"
              :class="systemHealth.database?.status === 'connected' ? 'bg-green-500' : 'bg-gray-300'"
            ></div>
          </div>
          <div class="mt-4 space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Tablas</span>
              <span class="font-medium">{{ systemHealth.database?.tables ?? '—' }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Tamaño</span>
              <span class="font-medium">{{ systemHealth.database?.size || '—' }}</span>
            </div>
          </div>
        </UiCard>

        <!-- Cache -->
        <UiCard padding="md">
          <div class="flex justify-between items-start">
            <div>
              <p class="text-sm text-gray-500">Cache (Redis)</p>
              <p class="text-2xl font-bold text-gray-900 mt-1">{{ systemHealth.cache?.status || '—' }}</p>
            </div>
            <div
              class="w-3 h-3 rounded-full"
              :class="systemHealth.cache?.status === 'connected' ? 'bg-green-500' : 'bg-gray-300'"
            ></div>
          </div>
          <div class="mt-4 space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Keys en cache</span>
              <span class="font-medium">{{ systemHealth.cache?.keys ?? '—' }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Hit rate</span>
              <span class="font-medium">{{ systemHealth.cache?.hit_rate ?? '—' }}</span>
            </div>
          </div>
        </UiCard>
      </div>
    </template>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <UiCard v-for="i in 3" :key="i" padding="md" class="animate-pulse">
        <div class="h-4 bg-gray-200 rounded w-24 mb-3"></div>
        <div class="h-8 bg-gray-200 rounded w-32 mb-4"></div>
        <div class="space-y-2">
          <div class="h-3 bg-gray-200 rounded w-20"></div>
          <div class="h-3 bg-gray-200 rounded w-28"></div>
        </div>
      </UiCard>
    </div>

    <!-- Environment Info -->
    <template v-if="envInfo">
      <UiCard padding="md">
        <h3 class="text-lg font-bold text-gray-900 mb-4">Información del Entorno</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="space-y-3">
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Environment</span>
              <span class="font-medium px-2 py-1 bg-gray-100 rounded">{{ envInfo.environment || '—' }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Debug Mode</span>
              <span class="font-medium" :class="envInfo.debug ? 'text-yellow-600' : 'text-green-600'">
                {{ envInfo.debug ? 'Activado' : 'Desactivado' }}
              </span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Timezone</span>
              <span class="font-medium">{{ envInfo.timezone || '—' }}</span>
            </div>
          </div>
          <div class="space-y-3">
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Python Version</span>
              <span class="font-medium">{{ envInfo.python_version || '—' }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">PostgreSQL</span>
              <span class="font-medium">{{ envInfo.postgresql_version || '—' }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Node.js</span>
              <span class="font-medium">{{ envInfo.node_version || '—' }}</span>
            </div>
          </div>
          <div class="space-y-3">
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">API URL</span>
              <span class="font-medium text-xs truncate max-w-[150px]">{{ envInfo.api_url || '—' }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Frontend URL</span>
              <span class="font-medium text-xs truncate max-w-[150px]">{{ envInfo.frontend_url || '—' }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Last Deploy</span>
              <span class="font-medium">{{ envInfo.last_deploy || '—' }}</span>
            </div>
          </div>
        </div>
      </UiCard>
    </template>

    <!-- Database Management -->
    <UiCard padding="none" class="overflow-hidden">
      <div class="p-6 border-b border-gray-200">
        <h3 class="text-lg font-bold text-gray-900">Base de Datos</h3>
      </div>
      <div class="p-6">
        <div class="flex gap-4">
          <button
            @click="runBackup"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            :disabled="backupInProgress"
          >
            <Database class="w-4 h-4 mr-1" />
            <span>{{ backupInProgress ? 'Generando...' : 'Backup Ahora' }}</span>
          </button>
          <button
            @click="confirmOptimize"
            class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
          >
            <Activity class="w-4 h-4 mr-1" />
            <span>Optimizar</span>
          </button>
          <button
            @click="showMigrations = true"
            class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
          >
            <RefreshCw class="w-4 h-4 mr-1" />
            <span>Migraciones</span>
          </button>
        </div>

        <!-- Backup History -->
        <div v-if="backups.length > 0" class="mt-6">
          <h4 class="font-medium text-gray-900 mb-3">Backups Recientes</h4>
          <div class="space-y-2">
            <div
              v-for="backup in backups"
              :key="backup.id"
              class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div class="flex items-center gap-3">
                <span class="text-2xl">💾</span>
                <div>
                  <p class="font-medium text-sm">{{ backup.filename }}</p>
                  <p class="text-xs text-gray-500">{{ formatDateTime(backup.created_at) }}</p>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-sm text-gray-500">{{ backup.size }}</span>
                <button
                  @click="downloadBackup(backup)"
                  class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                >
                  📥
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </UiCard>

    <!-- Cache Management -->
    <UiCard padding="none" class="overflow-hidden">
      <div class="p-6 border-b border-gray-200">
        <h3 class="text-lg font-bold text-gray-900">Gestión de Cache</h3>
      </div>
      <div class="p-6">
        <div class="flex gap-4">
          <button
            @click="confirmClearCache('all')"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            <Trash2 class="w-4 h-4 mr-1" />
            Limpiar Todo
          </button>
          <button
            @click="confirmClearCache('api')"
            class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            <RefreshCw class="w-4 h-4 mr-1" />
            Limpiar API
          </button>
          <button
            @click="confirmClearCache('static')"
            class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            <RefreshCw class="w-4 h-4 mr-1" />
            Limpiar Estático
          </button>
        </div>
      </div>
    </UiCard>

    <!-- Danger Zone -->
    <div class="bg-red-50 rounded-xl p-6 border border-red-200">
      <h3 class="text-lg font-bold text-red-700 mb-4 flex items-center gap-2">
        <span>⚠️</span> Zona de Peligro
      </h3>
      <div class="space-y-4">
        <div class="flex items-center justify-between p-4 bg-white rounded-lg border border-red-100">
          <div>
            <p class="font-medium text-gray-900">Forzar Logout Global</p>
            <p class="text-sm text-gray-500">Cerrar todas las sesiones activas de todos los usuarios</p>
          </div>
          <button
            @click="confirmForceLogout"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Ejecutar
          </button>
        </div>
        <div class="flex items-center justify-between p-4 bg-white rounded-lg border border-red-100">
          <div>
            <p class="font-medium text-gray-900">Resetear Cache de Sesiones</p>
            <p class="text-sm text-gray-500">Invalidar todos los tokens JWT activos</p>
          </div>
          <button
            @click="confirmResetSessions"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Ejecutar
          </button>
        </div>
      </div>
    </div>
    <!-- Confirm Dialog -->
    <UiConfirmDialog
      v-model="confirmData.show"
      :title="confirmData.title"
      :message="confirmData.message"
      :confirm-text="confirmData.confirmText"
      :variant="confirmData.variant"
      :loading="confirmLoading"
      @confirm="executeConfirmAction"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useHead } from '#app'
import {
  Rocket,
  Wrench,
  AlertTriangle,
  RefreshCw,
  Database,
  Server,
  Activity,
  CheckCircle,
  XCircle,
  Clock,
  ArrowRight,
  Download,
  Trash2,
  AlertCircle,
  Power,
  Save,
  Shield,
  Settings,
  Users,
  FileText,
  Globe
} from 'lucide-vue-next'

// @ts-expect-error Nuxt auto-import
definePageMeta({
  layout: 'superadmin',
  middleware: ['superadmin']
})

const api = useApi()
const toast = useToast()

const maintenanceMode = ref(false)
const backupInProgress = ref(false)
const backups = ref<any[]>([])
const showMigrations = ref(false)
const confirmLoading = ref(false)

const confirmData = ref<{
  show: boolean
  title: string
  message: string
  confirmText?: string
  variant?: 'danger' | 'warning' | 'info'
  action?: () => Promise<void>
}>({
  show: false,
  title: '',
  message: '',
  action: undefined,
})

function openConfirm(title: string, message: string, action: () => Promise<void>, options?: { confirmText?: string, variant?: 'danger' | 'warning' | 'info' }) {
  confirmData.value = { show: true, title, message, action, ...options }
}

async function executeConfirmAction() {
  if (!confirmData.value.action) return
  confirmLoading.value = true
  try {
    await confirmData.value.action()
  } finally {
    confirmLoading.value = false
    confirmData.value.show = false
    confirmData.value.action = undefined
  }
}

const systemHealth = ref<any>(null)

const envInfo = ref<any>(null)

const loadSystemHealth = async () => {
  try {
    const health = await api.get('/superadmin/system/health')
    systemHealth.value = health

    const env = await api.get('/superadmin/system/environment')
    maintenanceMode.value = env.maintenance_mode || false
    envInfo.value = env
  } catch (error) {
    console.error('Error loading system health:', error)
    systemHealth.value = null
    envInfo.value = null
  }
}

const loadBackups = async () => {
  try {
    const response = await api.get('/superadmin/system/backups')
    backups.value = response
  } catch (error) {
    console.error('Error loading backups:', error)
  }
}

const confirmToggleMaintenance = () => {
  const action = maintenanceMode.value ? 'Desactivar' : 'Activar'
  openConfirm(
    `${action} Modo Mantenimiento`,
    `¿Estás seguro de ${action.toLowerCase()} el modo mantenimiento?`,
    executeToggleMaintenance,
    { confirmText: `${action}`, variant: maintenanceMode.value ? 'warning' : 'danger' }
  )
}

const executeToggleMaintenance = async () => {
  try {
    await api.post('/superadmin/system/maintenance-mode', {
      enabled: !maintenanceMode.value,
      message: maintenanceMode.value ? undefined : 'Estamos realizando mantenimiento. Volveremos pronto.',
    })
    maintenanceMode.value = !maintenanceMode.value
  } catch (error) {
    console.error('Error toggling maintenance:', error)
  }
}

const runBackup = async () => {
  backupInProgress.value = true
  try {
    await api.post('/superadmin/system/backups/trigger')
    toast.success('Backup iniciado')
    await loadBackups()
  } catch (error) {
    console.error('Error running backup:', error)
    toast.error('Error al iniciar backup')
  } finally {
    backupInProgress.value = false
  }
}

const confirmOptimize = () => {
  openConfirm(
    'Optimizar Base de Datos',
    '¿Optimizar la base de datos? Esto puede tomar varios minutos.',
    executeOptimize,
    { confirmText: 'Optimizar', variant: 'warning' }
  )
}

const executeOptimize = async () => {
  try {
    await api.post('/superadmin/system/database/optimize')
    toast.success('Base de datos optimizada')
  } catch (error) {
    console.error('Error optimizing database:', error)
    toast.error('Función de optimización no disponible')
  }
}

let cacheTypeToClear = ''

const confirmClearCache = (type: string) => {
  cacheTypeToClear = type
  openConfirm(
    'Limpiar Cache',
    `¿Limpiar cache ${type === 'all' ? 'completa' : `de ${type}`}?`,
    executeClearCache,
    { confirmText: 'Limpiar', variant: 'danger' }
  )
}

const executeClearCache = async () => {
  try {
    await api.post('/superadmin/system/cache/flush', { type: cacheTypeToClear })
    toast.success('Cache limpiada')
  } catch (error) {
    console.error('Error clearing cache:', error)
    toast.error('Función de limpieza de cache no disponible')
  }
}

const confirmForceLogout = () => {
  openConfirm(
    'Forzar Logout Global',
    '¿FORZAR LOGOUT GLOBAL? Todos los usuarios serán desconectados.',
    executeForceLogout,
    { confirmText: 'Forzar Logout', variant: 'danger' }
  )
}

const executeForceLogout = async () => {
  try {
    await api.post('/superadmin/system/force-logout')
    toast.success('Logout global ejecutado')
  } catch (error) {
    console.error('Error forcing logout:', error)
    toast.error('Función de logout forzado no disponible')
  }
}

const confirmResetSessions = () => {
  openConfirm(
    'Resetear Cache de Sesiones',
    '¿Resetear cache de sesiones? Todos los tokens serán invalidados.',
    executeResetSessions,
    { confirmText: 'Resetear', variant: 'danger' }
  )
}

const executeResetSessions = async () => {
  try {
    await api.post('/superadmin/system/sessions/reset')
    toast.success('Sesiones reseteadas')
  } catch (error) {
    console.error('Error resetting sessions:', error)
    toast.error('Función de reset de sesiones no disponible')
  }
}

const downloadBackup = (backup: any) => {
  window.open(`${api.baseUrl}/superadmin/system/backups/${backup.id}/download`, '_blank')
}

const formatDateTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleString('es-CR')
}

onMounted(() => {
  loadSystemHealth()
  loadBackups()
})
</script>

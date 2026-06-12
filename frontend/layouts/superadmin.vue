<template>
  <div class="flex min-h-screen bg-gray-50">
    <!-- Skip to main content -->
    <a href="#main-content" class="skip-link">Ir al contenido principal</a>

    <!-- Mobile sidebar overlay -->
    <Transition name="fade">
      <div v-if="mobileOpen" class="fixed inset-0 bg-black/50 z-30 lg:hidden" @click="mobileOpen = false" />
    </Transition>

    <!-- Sidebar -->
    <aside
      class="w-64 bg-gradient-to-b from-primary-900 via-primary-800 to-emerald-900 text-white flex flex-col fixed h-full z-40 shadow-2xl transition-transform duration-300 lg:translate-x-0"
      :class="mobileOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <!-- Logo -->
      <div class="p-5 border-b border-white/10">
        <NuxtLink to="/superadmin/dashboard" class="flex items-center gap-3 hover:opacity-90 transition-opacity">
          <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-emerald-500 rounded-xl flex items-center justify-center shadow-lg">
            <Crown class="w-5 h-5 text-white" />
          </div>
          <div>
            <span class="font-bold text-white text-sm">Super Admin</span>
            <p class="text-xs text-primary-300">Panel de Control</p>
          </div>
        </NuxtLink>
      </div>
      
      <!-- Navigation -->
      <nav class="flex-1 py-4 overflow-y-auto" @click="mobileOpen = false">
        <!-- Principal -->
        <div class="mb-6">
          <p class="px-5 mb-3 text-[10px] font-bold text-primary-400 uppercase tracking-wider">Principal</p>
          <div class="mx-3 space-y-1">
              <NuxtLink 
                v-for="item in mainMenuItems" 
                :key="item.path"
                :to="item.path"
                class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 text-sm font-medium group"
                :class="$route.path === item.path 
                  ? 'bg-white/15 text-white border-l-2 border-primary-400 shadow-sm' 
                  : 'text-primary-100/80 hover:bg-white/10 hover:text-white border-l-2 border-transparent'"
                :aria-current="$route.path === item.path ? 'page' : undefined"
              >
                <component :is="item.icon" class="w-5 h-5" :class="$route.path === item.path ? 'text-primary-300' : 'text-primary-400/60 group-hover:text-primary-300'" />
                <span class="flex-1">{{ item.label }}</span>
                <span v-if="item.badge" class="bg-red-500/90 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                  {{ item.badge }}
                </span>
              </NuxtLink>
          </div>
        </div>

        <!-- Gestión -->
        <div class="mb-6">
          <p class="px-5 mb-3 text-[10px] font-bold text-primary-400 uppercase tracking-wider">Gestión</p>
          <div class="mx-3 space-y-1">
              <NuxtLink 
                v-for="item in managementMenuItems" 
                :key="item.path"
                :to="item.path"
                class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 text-sm font-medium group"
                :class="$route.path.startsWith(item.path)
                  ? 'bg-white/15 text-white border-l-2 border-primary-400 shadow-sm' 
                  : 'text-primary-100/80 hover:bg-white/10 hover:text-white border-l-2 border-transparent'"
                :aria-current="$route.path === item.path ? 'page' : undefined"
              >
                <component :is="item.icon" class="w-5 h-5" :class="$route.path.startsWith(item.path) ? 'text-primary-300' : 'text-primary-400/60 group-hover:text-primary-300'" />
                <span class="flex-1">{{ item.label }}</span>
              </NuxtLink>
          </div>
        </div>

        <!-- Monitoreo -->
        <div class="mb-6">
          <p class="px-5 mb-3 text-[10px] font-bold text-primary-400 uppercase tracking-wider">Monitoreo</p>
          <div class="mx-3 space-y-1">
              <NuxtLink 
                v-for="item in monitoringMenuItems" 
                :key="item.path"
                :to="item.path"
                class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 text-sm font-medium group"
                :class="$route.path.startsWith(item.path)
                  ? 'bg-white/15 text-white border-l-2 border-primary-400 shadow-sm' 
                  : 'text-primary-100/80 hover:bg-white/10 hover:text-white border-l-2 border-transparent'"
                :aria-current="$route.path === item.path ? 'page' : undefined"
              >
                <component :is="item.icon" class="w-5 h-5" :class="$route.path.startsWith(item.path) ? 'text-primary-300' : 'text-primary-400/60 group-hover:text-primary-300'" />
                <span class="flex-1">{{ item.label }}</span>
              </NuxtLink>
          </div>
        </div>

        <!-- Sistema -->
        <div>
          <p class="px-5 mb-3 text-[10px] font-bold text-primary-400 uppercase tracking-wider">Sistema</p>
          <div class="mx-3 space-y-1">
              <NuxtLink 
                v-for="item in systemMenuItems" 
                :key="item.path"
                :to="item.path"
                class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 text-sm font-medium group"
                :class="$route.path.startsWith(item.path)
                  ? 'bg-white/15 text-white border-l-2 border-primary-400 shadow-sm' 
                  : 'text-primary-100/80 hover:bg-white/10 hover:text-white border-l-2 border-transparent'"
                :aria-current="$route.path === item.path ? 'page' : undefined"
              >
                <component :is="item.icon" class="w-5 h-5" :class="$route.path.startsWith(item.path) ? 'text-primary-300' : 'text-primary-400/60 group-hover:text-primary-300'" />
                <span class="flex-1">{{ item.label }}</span>
              </NuxtLink>
          </div>
        </div>
      </nav>

      <!-- User Section -->
      <div class="p-4 border-t border-white/10">
        <div class="flex items-center gap-3 p-3 bg-white/10 rounded-xl hover:bg-white/15 transition-colors">
          <div class="w-9 h-9 bg-gradient-to-br from-primary-400 to-emerald-500 rounded-lg flex items-center justify-center text-white font-bold text-sm">
            {{ userInitials }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-white text-xs truncate">{{ user?.full_name }}</p>
            <p class="text-[10px] text-primary-300 capitalize">{{ user?.role?.replace('_', ' ') }}</p>
          </div>
          <button @click="logout" class="p-2 text-primary-300/60 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all">
            <LogOut class="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col lg:ml-64">
      <!-- Header -->
      <header class="bg-white border-b border-gray-200 px-4 sm:px-8 py-5 sticky top-0 z-10 shadow-sm">
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-3">
            <button
              class="lg:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition-colors"
              @click="mobileOpen = true"
              aria-label="Abrir menú"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div>
              <div class="flex items-center gap-4">
                <h1 class="text-2xl font-bold text-gray-900">{{ pageTitle }}</h1>
                <span class="px-4 py-1.5 bg-primary-100 text-primary-700 rounded-full text-xs font-bold uppercase tracking-wide">
                  Super Admin
                </span>
              </div>
              <p class="text-gray-500 text-sm mt-1">{{ currentDate }}</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <!-- Global Search -->
            <div class="relative">
              <input 
                v-model="searchQuery"
                @keyup.enter="handleSearch"
                type="text" 
                placeholder="Buscar usuarios, proveedores..." 
                class="pl-11 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 w-80 transition-all placeholder:text-gray-400"
              />
              <Search class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            </div>
            
            <!-- Quick Actions Dropdown -->
            <div class="relative" ref="quickActionsRef">
              <button 
                @click="showQuickActions = !showQuickActions"
                class="flex items-center gap-2 px-4 py-2.5 bg-primary-50 hover:bg-primary-100 text-primary-700 rounded-xl transition-colors font-medium text-sm"
              >
                <PlusCircle class="w-4 h-4" />
                <span>Nuevo</span>
                <ChevronDown class="w-4 h-4" />
              </button>
              
              <div v-if="showQuickActions" class="absolute right-0 top-full mt-2 w-56 bg-white rounded-xl shadow-xl border border-gray-200 py-2 z-50">
                <NuxtLink to="/superadmin/users" class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 text-sm text-gray-700">
                  <UserPlus class="w-4 h-4 text-primary-600" />
                  <span>Nuevo Usuario</span>
                </NuxtLink>
                <NuxtLink to="/superadmin/vendors" class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 text-sm text-gray-700">
                  <Store class="w-4 h-4 text-primary-600" />
                  <span>Nuevo Proveedor</span>
                </NuxtLink>
                <NuxtLink to="/superadmin/content" class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 text-sm text-gray-700">
                  <FileText class="w-4 h-4 text-primary-600" />
                  <span>Nuevo Artículo</span>
                </NuxtLink>
                <div class="border-t border-gray-100 my-2"></div>
                <NuxtLink to="/superadmin/properties" class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 text-sm text-gray-700">
                  <Building class="w-4 h-4 text-primary-600" />
                  <span>Nueva Propiedad</span>
                </NuxtLink>
              </div>
            </div>
            
            <!-- Notifications -->
            <button class="p-2.5 bg-gray-50 rounded-xl text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors relative">
              <Bell class="w-5 h-5" />
              <span class="absolute top-2 right-2 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-white"></span>
            </button>
            
            <!-- Emergency Actions -->
            <button 
              ref="emergencyBtnRef"
              @click="toggleEmergencyMenu"
              class="p-2.5 bg-red-50 hover:bg-red-100 rounded-xl text-red-600 transition-colors"
              title="Acciones de Emergencia"
            >
              <AlertTriangle class="w-5 h-5" />
            </button>
          </div>
        </div>

      </header>

      <!-- Page Content -->
      <div id="main-content" class="flex-1 overflow-y-auto overflow-x-auto p-8 bg-gray-50">
        <slot />
      </div>
    </main>

    <!-- Emergency Menu Dropdown (Teleported outside sticky header) -->
    <Teleport to="body">
      <div v-if="showEmergencyMenu" ref="emergencyMenuRef" class="fixed w-80 bg-white rounded-xl shadow-xl border border-red-200 p-5 z-50"
        :style="{ top: emergencyMenuPosition.top + 'px', right: emergencyMenuPosition.right + 'px' }">
        <h3 class="font-bold text-red-600 mb-4 flex items-center gap-2">
          <AlertTriangle class="w-5 h-5" />
          Acciones de Emergencia
        </h3>
        <div class="space-y-2">
          <button 
            @click="triggerMaintenanceMode"
            :disabled="maintenanceLoading"
            class="w-full p-4 bg-red-50 hover:bg-red-100 rounded-xl text-left text-sm text-red-700 transition-colors flex items-start gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Loader2 v-if="maintenanceLoading" class="w-5 h-5 mt-0.5 animate-spin" />
            <Power v-else class="w-5 h-5 mt-0.5" />
            <div>
              <span class="font-semibold">Modo Mantenimiento</span>
              <p class="text-xs text-red-500 mt-0.5">Desactivar sitio público</p>
            </div>
          </button>
          <button 
            @click="forceGlobalLogout"
            :disabled="logoutLoading"
            class="w-full p-4 bg-orange-50 hover:bg-orange-100 rounded-xl text-left text-sm text-orange-700 transition-colors flex items-start gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Loader2 v-if="logoutLoading" class="w-5 h-5 mt-0.5 animate-spin" />
            <LogOut v-else class="w-5 h-5 mt-0.5" />
            <div>
              <span class="font-semibold">Forzar Logout Global</span>
              <p class="text-xs text-orange-500 mt-0.5">Cerrar todas las sesiones</p>
            </div>
          </button>
          <button 
            @click="blockSuspiciousIPs"
            :disabled="blockIPsLoading"
            class="w-full p-4 bg-amber-50 hover:bg-amber-100 rounded-xl text-left text-sm text-amber-700 transition-colors flex items-start gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Loader2 v-if="blockIPsLoading" class="w-5 h-5 mt-0.5 animate-spin" />
            <Shield v-else class="w-5 h-5 mt-0.5" />
            <div>
              <span class="font-semibold">Bloquear IPs Sospechosas</span>
              <p class="text-xs text-amber-600 mt-0.5">Bloquear intentos de ataque</p>
            </div>
          </button>
          <div class="border-t border-gray-200 my-3"></div>
          <button 
            @click="clearSystemCache"
            :disabled="clearCacheLoading"
            class="w-full p-4 bg-blue-50 hover:bg-blue-100 rounded-xl text-left text-sm text-blue-700 transition-colors flex items-start gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Loader2 v-if="clearCacheLoading" class="w-5 h-5 mt-0.5 animate-spin" />
            <RefreshCw v-else class="w-5 h-5 mt-0.5" />
            <div>
              <span class="font-semibold">Limpiar Caché</span>
              <p class="text-xs text-blue-500 mt-0.5">Refrescar caché del sistema</p>
            </div>
          </button>
        </div>
      </div>
    </Teleport>

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
import { computed, ref, onMounted, nextTick } from 'vue'
import { onClickOutside } from '@vueuse/core'
import { 
  LayoutDashboard, 
  Users, 
  Store, 
  Building2, 
  Calendar, 
  Car, 
  FileText, 
  MapPin, 
  Star,
  BarChart3,
  FileBarChart2,
  CreditCard,
  ScrollText,
  Settings,
  Cog,
  Search,
  PlusCircle,
  ChevronDown,
  UserPlus,
  Building,
  Bell,
  AlertTriangle,
  Power,
  LogOut,
  Shield,
  RefreshCw,
  LayoutGrid,
  Crown,
  Loader2
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const user = computed(() => auth.user)
const mobileOpen = ref(false)
const showEmergencyMenu = ref(false)
const showQuickActions = ref(false)
const emergencyMenuRef = ref<HTMLElement | null>(null)
const emergencyBtnRef = ref<HTMLElement | null>(null)
const quickActionsRef = ref<HTMLElement | null>(null)
const searchQuery = ref('')
const emergencyMenuPosition = ref({ top: 0, right: 0 })

const maintenanceLoading = ref(false)
const logoutLoading = ref(false)
const blockIPsLoading = ref(false)
const clearCacheLoading = ref(false)

const pendingVendorCount = ref(0)

onClickOutside(quickActionsRef, () => {
  showQuickActions.value = false
})

const toggleEmergencyMenu = async () => {
  if (!showEmergencyMenu.value && emergencyBtnRef.value) {
    const rect = emergencyBtnRef.value.getBoundingClientRect()
    emergencyMenuPosition.value = {
      top: rect.bottom + 8,
      right: window.innerWidth - rect.right
    }
  }
  showEmergencyMenu.value = !showEmergencyMenu.value
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    navigateTo(`/superadmin/search?q=${encodeURIComponent(searchQuery.value)}`)
    searchQuery.value = ''
  }
}

const userInitials = computed(() => {
  if (!user.value?.full_name) return '?'
  return user.value.full_name.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2)
})

const currentDate = computed(() => {
  return new Date().toLocaleDateString('es-CR', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})

const pageTitle = computed(() => {
  const path = route.path
  const titles: Record<string, string> = {
    '/superadmin/dashboard': 'Dashboard',
    '/superadmin/users': 'Usuarios',
    '/superadmin/users/activity': 'Actividad de Usuarios',
    '/superadmin/admins': 'Administradores',
    '/superadmin/vendors': 'Proveedores',
    '/superadmin/vendors/pending': 'Aprobación de Proveedores',
    '/superadmin/properties': 'Propiedades',
    '/superadmin/bookings': 'Reservas',
    '/superadmin/bookings/refunds': 'Reembolsos',
    '/superadmin/fleet': 'Flota',
    '/superadmin/fleet/vehicles': 'Vehículos',
    '/superadmin/fleet/boats': 'Botes',
    '/superadmin/content': 'Contenido',
    '/superadmin/destinations': 'Destinos',
    '/superadmin/reviews': 'Reviews',
    '/superadmin/analytics': 'Analytics',
    '/superadmin/reports': 'Reportes',
    '/superadmin/pos': 'Puntos de Venta',
    '/superadmin/audit': 'Auditoría',
    '/superadmin/system': 'Sistema',
    '/superadmin/settings': 'Configuración',
  }
  if (path.startsWith('/superadmin/users/') && path !== '/superadmin/users') {
    return 'Detalle de Usuario'
  }
  if (path.startsWith('/superadmin/vendors/') && path.includes('/documents')) {
    return 'Verificación de Documentos'
  }
  return titles[path] || 'Super Admin'
})

const mainMenuItems = computed(() => [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/superadmin/dashboard', badge: null },
  { icon: Users, label: 'Usuarios', path: '/superadmin/users', badge: null },
  { icon: Store, label: 'Proveedores', path: '/superadmin/vendors', badge: pendingVendorCount.value || null },
])

const managementMenuItems = [
  { icon: Building2, label: 'Propiedades', path: '/superadmin/properties' },
  { icon: Calendar, label: 'Reservas', path: '/superadmin/bookings' },
  { icon: Car, label: 'Flota', path: '/superadmin/fleet' },
  { icon: FileText, label: 'Contenido', path: '/superadmin/content' },
  { icon: MapPin, label: 'Destinos', path: '/superadmin/destinations' },
  { icon: Star, label: 'Reviews', path: '/superadmin/reviews' },
]

const monitoringMenuItems = [
  { icon: BarChart3, label: 'Analytics', path: '/superadmin/analytics' },
  { icon: FileBarChart2, label: 'Reportes', path: '/superadmin/reports' },
  { icon: CreditCard, label: 'Puntos de Venta', path: '/superadmin/pos' },
  { icon: ScrollText, label: 'Auditoría', path: '/superadmin/audit' },
]

const systemMenuItems = [
  { icon: Cog, label: 'Sistema', path: '/superadmin/system' },
  { icon: Settings, label: 'Configuración', path: '/superadmin/settings' },
]

const logout = () => {
  auth.logout()
  router.push('/login')
}

watch(() => route?.path, () => { mobileOpen.value = false })

onClickOutside(emergencyMenuRef, () => {
  showEmergencyMenu.value = false
}, { ignore: [emergencyBtnRef] })

onMounted(() => {
  auth.initAuth()
  if (!auth.isAuthenticated || auth.user?.role !== 'super_admin') {
    router.push('/login')
  }
})

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

const triggerMaintenanceMode = () => {
  openConfirm(
    'Modo Mantenimiento',
    '¿Estás seguro de activar el modo mantenimiento?',
    executeTriggerMaintenance,
    { confirmText: 'Activar', variant: 'danger' }
  )
}

const executeTriggerMaintenance = async () => {
  maintenanceLoading.value = true
  try {
    const api = useApi()
    await api.post('/superadmin/system/maintenance', { enabled: true })
    toast.success('Modo mantenimiento activado')
    showEmergencyMenu.value = false
  } finally {
    maintenanceLoading.value = false
  }
}

const forceGlobalLogout = () => {
  openConfirm(
    'Cierre de Sesiones',
    '¿Forzar cierre de todas las sesiones?',
    executeForceGlobalLogout,
    { confirmText: 'Forzar Cierre', variant: 'danger' }
  )
}

const executeForceGlobalLogout = async () => {
  logoutLoading.value = true
  try {
    const api = useApi()
    await api.post('/superadmin/system/logout-all')
    toast.success('Todas las sesiones han sido cerradas')
    showEmergencyMenu.value = false
  } finally {
    logoutLoading.value = false
  }
}

const blockSuspiciousIPs = async () => {
  blockIPsLoading.value = true
  try {
    const api = useApi()
    await api.post('/superadmin/security/block-suspicious')
    toast.success('IPs sospechosas bloqueadas')
  } catch (error) {
    toast.error('Error al bloquear IPs')
  } finally {
    blockIPsLoading.value = false
    showEmergencyMenu.value = false
  }
}

const clearSystemCache = async () => {
  clearCacheLoading.value = true
  try {
    const api = useApi()
    await api.post('/superadmin/system/clear-cache')
    toast.success('Caché del sistema limpiada')
  } catch (error) {
    toast.error('Error al limpiar caché')
  } finally {
    clearCacheLoading.value = false
    showEmergencyMenu.value = false
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
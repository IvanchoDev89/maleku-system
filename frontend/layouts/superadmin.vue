<template>
  <div class="flex min-h-screen bg-gray-50 dark:bg-gray-950 transition-colors">
    <!-- Skip to main content -->
    <a href="#main-content" class="skip-link">Ir al contenido principal</a>

    <!-- Mobile sidebar overlay -->
    <Transition name="fade">
      <div v-if="mobileOpen" class="fixed inset-0 bg-black/50 z-30 lg:hidden" @click="mobileOpen = false" />
    </Transition>

    <!-- Sidebar -->
    <aside
      class="bg-gradient-to-b from-primary-900 via-primary-800 to-emerald-900 text-white flex flex-col fixed h-full z-40 shadow-2xl transition-all duration-300"
      :class="[sidebarCollapsed ? 'w-20' : 'w-64', mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0']"
    >
      <!-- Logo -->
      <div class="p-5 border-b border-white/10 flex items-center justify-between">
        <NuxtLink to="/superadmin/dashboard" class="flex items-center gap-3 hover:opacity-90 transition-opacity min-w-0" :class="sidebarCollapsed ? 'justify-center w-full' : ''">
          <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-emerald-500 rounded-xl flex items-center justify-center shadow-lg shrink-0">
            <Crown class="w-5 h-5 text-white" />
          </div>
          <div v-if="!sidebarCollapsed" class="min-w-0">
            <span class="font-bold text-white text-sm block truncate">Super Admin</span>
            <p class="text-xs text-primary-300 truncate">Panel de Control</p>
          </div>
        </NuxtLink>
        <button
          v-if="!sidebarCollapsed"
          @click="sidebarCollapsed = true"
          class="hidden lg:flex p-1.5 rounded-lg text-primary-300 hover:bg-white/10 transition-colors shrink-0"
          title="Colapsar menú"
        >
          <ChevronLeft class="w-4 h-4" />
        </button>
      </div>

      <!-- Collapse toggle for collapsed state -->
      <button
        v-if="sidebarCollapsed"
        @click="sidebarCollapsed = false"
        class="hidden lg:flex absolute -right-3 top-20 w-6 h-6 bg-primary-700 border-2 border-primary-900 rounded-full items-center justify-center text-white hover:bg-primary-600 transition-colors z-50 shadow-md"
        title="Expandir menú"
      >
        <ChevronRight class="w-3 h-3" />
      </button>

      <!-- Navigation -->
      <nav class="flex-1 py-4 overflow-y-auto overflow-x-hidden" @click="mobileOpen = false">
        <template v-for="(group, gIndex) in navGroups" :key="gIndex">
          <div class="mb-6">
            <p v-if="!sidebarCollapsed" class="px-5 mb-3 text-[10px] font-bold text-primary-400 uppercase tracking-wider truncate">{{ group.label }}</p>
            <div class="mx-3 space-y-1">
              <NuxtLink
                v-for="item in group.items"
                :key="item.path"
                :to="item.path"
                class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 text-sm font-medium group"
                :class="[
                  isActive(item.path)
                    ? 'bg-white/15 text-white border-l-2 border-primary-400 shadow-sm'
                    : 'text-primary-100/80 hover:bg-white/10 hover:text-white border-l-2 border-transparent',
                  sidebarCollapsed ? 'justify-center px-2 border-l-0' : ''
                ]"
                :aria-current="isActive(item.path) ? 'page' : undefined"
              >
                <component :is="item.icon" class="w-5 h-5 shrink-0" :class="isActive(item.path) ? 'text-primary-300' : 'text-primary-400/60 group-hover:text-primary-300'" />
                <span v-if="!sidebarCollapsed" class="flex-1 truncate">{{ item.label }}</span>
                <span v-if="item.badge && !sidebarCollapsed" class="bg-red-500/90 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                  {{ item.badge }}
                </span>
              </NuxtLink>
            </div>
          </div>
        </template>
      </nav>

      <!-- User Section -->
      <div class="p-4 border-t border-white/10">
        <div class="flex items-center gap-3 p-3 bg-white/10 rounded-xl hover:bg-white/15 transition-colors" :class="sidebarCollapsed ? 'justify-center p-2' : ''">
          <div class="w-9 h-9 bg-gradient-to-br from-primary-400 to-emerald-500 rounded-lg flex items-center justify-center text-white font-bold text-sm shrink-0 relative">
            {{ userInitials }}
            <span class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-primary-800" :class="apiConnected ? 'bg-green-400' : 'bg-red-400'"></span>
          </div>
          <div v-if="!sidebarCollapsed" class="flex-1 min-w-0">
            <p class="font-medium text-white text-xs truncate">{{ user?.full_name }}</p>
            <p class="text-[10px] text-primary-300 capitalize truncate">{{ user?.role?.replace('_', ' ') }}</p>
          </div>
          <button @click="logout" class="p-2 text-primary-300/60 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all shrink-0" title="Cerrar sesión">
            <LogOut class="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col min-h-screen" :class="sidebarCollapsed ? 'lg:ml-20' : 'lg:ml-64'">
      <!-- Header -->
      <header class="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 px-4 sm:px-8 py-4 sticky top-0 z-10 shadow-sm transition-colors">
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-3 min-w-0">
            <button
              class="lg:hidden p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              @click="mobileOpen = true"
              aria-label="Abrir menú"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div class="min-w-0">
              <div class="flex items-center gap-3">
                <h1 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white truncate">{{ pageTitle }}</h1>
                <span class="hidden sm:inline px-3 py-1 bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 rounded-full text-xs font-bold uppercase tracking-wide shrink-0">
                  Super Admin
                </span>
              </div>
              <!-- Breadcrumbs -->
              <nav class="flex items-center gap-1.5 text-xs text-gray-400 dark:text-gray-500 mt-0.5" aria-label="Breadcrumb">
                <NuxtLink to="/superadmin/dashboard" class="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">Inicio</NuxtLink>
                <template v-for="(crumb, idx) in breadcrumbs" :key="idx">
                  <ChevronRight class="w-3 h-3" />
                  <NuxtLink
                    v-if="crumb.path"
                    :to="crumb.path"
                    class="hover:text-primary-600 dark:hover:text-primary-400 transition-colors truncate max-w-[120px]"
                  >
                    {{ crumb.label }}
                  </NuxtLink>
                  <span v-else class="text-gray-600 dark:text-gray-300 truncate max-w-[120px]">{{ crumb.label }}</span>
                </template>
              </nav>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <!-- Global Search -->
            <div class="hidden md:block relative">
              <input
                ref="searchInputRef"
                v-model="searchQuery"
                @keyup.enter="handleSearch"
                type="text"
                placeholder="Buscar... (⌘K)"
                class="pl-10 pr-10 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 w-48 lg:w-64 transition-all placeholder:text-gray-400 dark:placeholder:text-gray-500 text-gray-900 dark:text-white"
              />
              <Search class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500" />
              <kbd class="absolute right-3 top-1/2 -translate-y-1/2 hidden sm:inline-flex items-center px-1.5 py-0.5 text-[10px] text-gray-400 bg-gray-200 dark:bg-gray-700 rounded font-mono">⌘K</kbd>
            </div>

            <!-- Quick Actions Dropdown -->
            <div class="relative" ref="quickActionsRef">
              <button
                @click="showQuickActions = !showQuickActions"
                class="flex items-center gap-2 px-4 py-2 bg-primary-50 dark:bg-primary-900/50 hover:bg-primary-100 dark:hover:bg-primary-900 text-primary-700 dark:text-primary-300 rounded-xl transition-colors font-medium text-sm"
              >
                <PlusCircle class="w-4 h-4" />
                <span class="hidden sm:inline">Nuevo</span>
                <ChevronDown class="w-4 h-4" />
              </button>

              <div v-if="showQuickActions" class="absolute right-0 top-full mt-2 w-56 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 py-2 z-50">
                <NuxtLink to="/superadmin/users" class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 text-sm text-gray-700 dark:text-gray-300">
                  <UserPlus class="w-4 h-4 text-primary-600" />
                  <span>Nuevo Usuario</span>
                </NuxtLink>
                <NuxtLink to="/superadmin/vendors" class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 text-sm text-gray-700 dark:text-gray-300">
                  <Store class="w-4 h-4 text-primary-600" />
                  <span>Nuevo Proveedor</span>
                </NuxtLink>
                <NuxtLink to="/superadmin/content" class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 text-sm text-gray-700 dark:text-gray-300">
                  <FileText class="w-4 h-4 text-primary-600" />
                  <span>Nuevo Artículo</span>
                </NuxtLink>
                <div class="border-t border-gray-100 dark:border-gray-700 my-2"></div>
                <NuxtLink to="/superadmin/properties" class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 text-sm text-gray-700 dark:text-gray-300">
                  <Building class="w-4 h-4 text-primary-600" />
                  <span>Nueva Propiedad</span>
                </NuxtLink>
              </div>
            </div>

            <!-- Dark Mode Toggle -->
            <button
              @click="toggleDarkMode"
              class="p-2.5 rounded-xl text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              :title="isDark ? 'Modo claro' : 'Modo oscuro'"
            >
              <Sun v-if="isDark" class="w-5 h-5" />
              <Moon v-else class="w-5 h-5" />
            </button>

            <!-- Notifications -->
            <button title="Notificaciones" class="p-2.5 bg-gray-50 dark:bg-gray-800 rounded-xl text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors relative">
              <Bell class="w-5 h-5" />
              <span v-if="notificationCount > 0" class="absolute top-2 right-2 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-white dark:border-gray-800"></span>
            </button>

            <!-- Emergency Actions -->
            <button
              ref="emergencyBtnRef"
              @click="toggleEmergencyMenu"
              class="p-2.5 bg-red-50 dark:bg-red-900/30 hover:bg-red-100 dark:hover:bg-red-900/50 rounded-xl text-red-600 dark:text-red-400 transition-colors"
              title="Acciones de Emergencia"
            >
              <AlertTriangle class="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <div id="main-content" class="flex-1 overflow-y-auto overflow-x-auto p-8 bg-gray-50 dark:bg-gray-950 transition-colors">
        <div v-if="!apiConnected" class="mb-6 px-4 py-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl flex items-center gap-3 text-sm text-red-700 dark:text-red-300">
          <AlertTriangle class="w-4 h-4 shrink-0" />
          <span>API no disponible — revisa que el backend esté corriendo en <code class="font-mono text-xs bg-red-100 dark:bg-red-900/40 px-1.5 py-0.5 rounded">localhost:8000</code></span>
        </div>
        <slot />
      </div>
    </main>

    <!-- Emergency Menu Dropdown -->
    <Teleport to="body">
      <div v-if="showEmergencyMenu" ref="emergencyMenuRef" class="fixed w-80 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-red-200 dark:border-red-900 p-5 z-50"
        :style="{ top: emergencyMenuPosition.top + 'px', right: emergencyMenuPosition.right + 'px' }">
        <h3 class="font-bold text-red-600 dark:text-red-400 mb-4 flex items-center gap-2">
          <AlertTriangle class="w-5 h-5" />
          Acciones de Emergencia
        </h3>
        <div class="space-y-2">
          <button
            @click="triggerMaintenanceMode"
            :disabled="maintenanceLoading"
            class="w-full p-4 bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/40 rounded-xl text-left text-sm text-red-700 dark:text-red-300 transition-colors flex items-start gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
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
            class="w-full p-4 bg-orange-50 dark:bg-orange-900/20 hover:bg-orange-100 dark:hover:bg-orange-900/40 rounded-xl text-left text-sm text-orange-700 dark:text-orange-300 transition-colors flex items-start gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
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
            class="w-full p-4 bg-amber-50 dark:bg-amber-900/20 hover:bg-amber-100 dark:hover:bg-amber-900/40 rounded-xl text-left text-sm text-amber-700 dark:text-amber-300 transition-colors flex items-start gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Loader2 v-if="blockIPsLoading" class="w-5 h-5 mt-0.5 animate-spin" />
            <Shield v-else class="w-5 h-5 mt-0.5" />
            <div>
              <span class="font-semibold">Bloquear IPs Sospechosas</span>
              <p class="text-xs text-amber-600 mt-0.5">Bloquear intentos de ataque</p>
            </div>
          </button>
          <div class="border-t border-gray-200 dark:border-gray-700 my-3"></div>
          <button
            @click="clearSystemCache"
            :disabled="clearCacheLoading"
            class="w-full p-4 bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/40 rounded-xl text-left text-sm text-blue-700 dark:text-blue-300 transition-colors flex items-start gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
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
import { onClickOutside } from '@vueuse/core'
import {
  LayoutDashboard,
  Users,
  Store,
  Building2,
  Compass,
  Calendar,
  Car,
  FileText,
  MapPin,
  Star,
  BarChart3,
  FileBarChart2,
  ScrollText,
  Crown,
  Cog,
  Settings,
  LogOut,
  Menu,
  Search,
  Bell,
  Shield,
  ChevronDown,
  Activity,
  AlertTriangle,
  RefreshCw,
  Ban,
  Trash2,
  Download,
  PlusCircle,
  UserPlus,
  Building,
  Loader2,
  Power,
  ChevronLeft,
  ChevronRight,
  Sun,
  Moon,
  Globe,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const colorMode = useColorMode()

const isDark = computed(() => colorMode.value === 'dark')

function toggleDarkMode() {
  colorMode.preference = isDark.value ? 'light' : 'dark'
}

const user = computed(() => auth.user)
const mobileOpen = ref(false)
const sidebarCollapsed = ref(false)
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
const { count: notificationCount, startPolling, stopPolling } = useNotifications()
const apiConnected = ref(true)

const checkApiHealth = async () => {
  try {
    const api = useApi()
    await api.get('/health')
    apiConnected.value = true
  } catch {
    apiConnected.value = false
  }
}

let healthInterval: ReturnType<typeof setInterval> | null = null

// Restore sidebar state from localStorage
onMounted(() => {
  const saved = localStorage.getItem('superadmin_sidebar_collapsed')
  if (saved) sidebarCollapsed.value = saved === 'true'
  startPolling()
  checkApiHealth()
  healthInterval = setInterval(checkApiHealth, 30000)

  const handler = (e: KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault()
      searchInputRef.value?.focus()
    }
  }
  document.addEventListener('keydown', handler)
  onUnmounted(() => document.removeEventListener('keydown', handler))
})

onUnmounted(() => {
  if (healthInterval) {
    clearInterval(healthInterval)
    healthInterval = null
  }
})

watch(sidebarCollapsed, (val) => {
  localStorage.setItem('superadmin_sidebar_collapsed', String(val))
})

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

const searchInputRef = ref<HTMLInputElement | null>(null)

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    navigateTo(`/superadmin/search?q=${encodeURIComponent(searchQuery.value.trim())}`)
    searchQuery.value = ''
  }
}

const userInitials = computed(() => {
  if (!user.value?.full_name) return '?'
  return user.value.full_name.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2)
})

function isActive(path: string): boolean {
  return route.path === path || route.path.startsWith(path + '/')
}

// Breadcrumbs
const breadcrumbs = computed(() => {
  const path = route.path
  const parts = path.split('/').filter(Boolean)
  const crumbs: { label: string; path?: string }[] = []
  let current = ''

  const titleMap: Record<string, string> = {
    dashboard: 'Dashboard',
    users: 'Usuarios',
    admins: 'Administradores',
    vendors: 'Proveedores',
    properties: 'Propiedades',
    bookings: 'Reservas',
    fleet: 'Flota',
    vehicles: 'Vehículos',
    boats: 'Botes',
    transportation: 'Transporte',
    flights: 'Vuelos',
    content: 'Contenido',
    destinations: 'Destinos',
    reviews: 'Reviews',
    analytics: 'Analytics',
    reports: 'Reportes',
    pos: 'Puntos de Venta',
    audit: 'Auditoría',
    system: 'Sistema',
    settings: 'Configuración',
    search: 'Búsqueda',
    pending: 'Pendientes',
    documents: 'Documentos',
    blog: 'Blog',
    pages: 'Páginas',
    media: 'Multimedia',
    seo: 'SEO',
    refunds: 'Reembolsos',
  }

  for (let i = 2; i < parts.length; i++) {
    const part = parts[i]
    current += '/' + part
    const label = titleMap[part] || part.charAt(0).toUpperCase() + part.slice(1)
    crumbs.push({ label, path: i < parts.length - 1 ? current : undefined })
  }

  return crumbs
})

const pageTitle = computed(() => {
  const path = route.path
  const titles: Record<string, string> = {
    '/superadmin/dashboard': 'Dashboard',
    '/superadmin/users': 'Usuarios',
    '/superadmin/admins': 'Administradores',
    '/superadmin/vendors': 'Proveedores',
    '/superadmin/vendors/pending': 'Aprobación de Proveedores',
    '/superadmin/properties': 'Propiedades',
    '/superadmin/bookings': 'Reservas',
    '/superadmin/bookings/refunds': 'Reembolsos',
    '/superadmin/fleet': 'Flota',
    '/superadmin/fleet/vehicles': 'Vehículos',
    '/superadmin/fleet/boats': 'Botes',
    '/superadmin/fleet/transportation': 'Transporte',
    '/superadmin/fleet/flights': 'Vuelos',
    '/superadmin/content': 'Contenido',
    '/superadmin/content/seo': 'SEO Global',
    '/superadmin/destinations': 'Destinos',
    '/superadmin/reviews': 'Reviews',
    '/superadmin/analytics': 'Analytics',
    '/superadmin/reports': 'Reportes',
    '/superadmin/pos': 'Puntos de Venta',
    '/superadmin/audit': 'Auditoría',
    '/superadmin/system': 'Sistema',
    '/superadmin/settings': 'Configuración',
    '/superadmin/search': 'Búsqueda',
  }
  if (path.startsWith('/superadmin/users/') && path !== '/superadmin/users') {
    return 'Detalle de Usuario'
  }
  if (path.startsWith('/superadmin/vendors/') && path.includes('/documents')) {
    return 'Verificación de Documentos'
  }
  return titles[path] || 'Super Admin'
})

// Navigation groups
interface NavItem {
  icon: any
  label: string
  path: string
  badge: number | null
}

interface NavGroup {
  label: string
  items: NavItem[]
}

const navGroups = computed<NavGroup[]>(() => [
  {
    label: 'Principal',
    items: [
      { icon: LayoutDashboard, label: 'Dashboard', path: '/superadmin/dashboard', badge: null },
      { icon: Users, label: 'Usuarios', path: '/superadmin/users', badge: null },
      { icon: Store, label: 'Proveedores', path: '/superadmin/vendors', badge: pendingVendorCount.value || null },
    ],
  },
  {
    label: 'Gestión',
    items: [
      { icon: Building2, label: 'Propiedades', path: '/superadmin/properties', badge: null },
      { icon: Compass, label: 'Tours', path: '/superadmin/tours', badge: null },
      { icon: Calendar, label: 'Reservas', path: '/superadmin/bookings', badge: null },
      { icon: Car, label: 'Flota', path: '/superadmin/fleet', badge: null },
      { icon: FileText, label: 'Contenido', path: '/superadmin/content', badge: null },
      { icon: Globe, label: 'SEO', path: '/superadmin/content/seo', badge: null },
      { icon: MapPin, label: 'Destinos', path: '/superadmin/destinations', badge: null },
      { icon: Star, label: 'Reviews', path: '/superadmin/reviews', badge: null },
    ],
  },
  {
    label: 'Monitoreo',
    items: [
      { icon: BarChart3, label: 'Analytics', path: '/superadmin/analytics', badge: null },
      { icon: FileBarChart2, label: 'Reportes', path: '/superadmin/reports', badge: null },
      { icon: ScrollText, label: 'Auditoría', path: '/superadmin/audit', badge: null },
    ],
  },
  {
    label: 'Sistema',
    items: [
      { icon: Cog, label: 'Sistema', path: '/superadmin/system', badge: null },
      { icon: Settings, label: 'Configuración', path: '/superadmin/settings', badge: null },
    ],
  },
])

const logout = () => {
  stopPolling()
  auth.logout()
  router.push('/login')
}

watch(() => route?.path, () => { mobileOpen.value = false })

onClickOutside(emergencyMenuRef, () => {
  showEmergencyMenu.value = false
}, { ignore: [emergencyBtnRef] })

// Confirm Dialog
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

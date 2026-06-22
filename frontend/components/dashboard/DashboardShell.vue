<template>
  <div class="flex min-h-screen bg-gray-50">
    <a href="#main-content" class="skip-link">Ir al contenido principal</a>

    <Transition name="fade">
      <div v-if="mobileOpen" class="fixed inset-0 bg-black/50 z-30 lg:hidden" @click="mobileOpen = false" />
    </Transition>

    <aside
      v-if="showSidebar"
      class="w-64 flex flex-col fixed h-full z-40 transition-transform duration-300 lg:translate-x-0"
      :class="[sidebarTheme, mobileOpen ? 'translate-x-0' : '-translate-x-full']"
    >
      <div class="p-4" :class="sidebarBorderClass">
        <NuxtLink to="/" class="flex items-center gap-3 hover:opacity-90 transition-opacity">
          <div class="w-9 h-9 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
            <Icon name="lucide:tree-palm" class="w-5 h-5 text-white" />
          </div>
          <div>
            <span :class="logoTitleClass">{{ logoTitle }}</span>
            <p :class="logoSubtitleClass">{{ logoSubtitle }}</p>
          </div>
        </NuxtLink>
      </div>

      <nav class="flex-1 py-4 overflow-y-auto">
        <div class="mb-6">
          <p class="px-4 mb-2 text-[10px] font-bold uppercase tracking-wider" :class="navGroupLabelClass">Principal</p>
          <div class="mx-2 space-y-0.5">
            <NuxtLink
              v-for="item in mainMenuItems"
              :key="item.path"
              :to="item.path"
              class="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 text-sm font-medium group border-l-2"
              :class="navLinkClass(item.path, true)"
              :aria-current="route.path === item.path ? 'page' : undefined"
              @click="mobileOpen = false"
            >
              <Icon :name="item.icon" class="w-5 h-5 flex-shrink-0" />
              <span class="flex-1">{{ item.label }}</span>
            </NuxtLink>
          </div>
        </div>
        <div class="mb-6">
          <p class="px-4 mb-2 text-[10px] font-bold uppercase tracking-wider" :class="navGroupLabelClass">Gestión</p>
          <div class="mx-2 space-y-0.5">
            <NuxtLink
              v-for="item in managementMenuItems"
              :key="item.path"
              :to="item.path"
              class="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 text-sm font-medium group border-l-2"
              :class="navLinkClass(item.path, false)"
              :aria-current="route.path.startsWith(item.path) ? 'page' : undefined"
              @click="mobileOpen = false"
            >
              <Icon :name="item.icon" class="w-5 h-5 flex-shrink-0" />
              <span class="flex-1">{{ item.label }}</span>
            </NuxtLink>
          </div>
        </div>
      </nav>

      <div class="p-4" :class="sidebarBorderClass">
        <div class="flex items-center gap-3 mb-3" :class="userSectionBgClass">
          <div :class="avatarClass">{{ userInitials }}</div>
          <div class="flex-1 min-w-0">
            <p :class="userNameClass">{{ user?.full_name || 'Usuario' }}</p>
            <p :class="userDetailClass">{{ userDetail }}</p>
          </div>
        </div>
        <button
          @click="logout"
          class="flex items-center gap-3 px-3 py-2 rounded-lg w-full transition-colors text-sm"
          :class="logoutClass"
        >
          <Icon name="lucide:log-out" class="w-4 h-4" />
          <span>{{ isVendor ? 'Cerrar Sesión' : 'Cerrar sesión' }}</span>
        </button>
      </div>
    </aside>

    <main class="flex-1 min-h-screen flex flex-col" :class="mainMarginClass">
      <header v-if="showHeader" class="bg-white border-b border-gray-200 px-4 sm:px-8 py-4 sticky top-0 z-10">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <button
              class="lg:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition-colors"
              @click="mobileOpen = true"
              aria-label="Abrir menú"
            >
              <Icon name="lucide:menu" class="w-5 h-5" />
            </button>
            <div>
              <h1 class="text-xl sm:text-2xl font-bold text-gray-900">{{ pageTitle }}</h1>
              <p class="text-xs text-gray-500 mt-0.5 hidden sm:block">{{ formattedDate }}</p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <div v-if="isAdmin" class="hidden md:block relative">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Buscar usuarios..."
                class="pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400 w-48 lg:w-64"
                @keyup.enter="handleSearch"
              />
              <Icon name="lucide:search" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            </div>
            <div class="relative" ref="notifRef">
              <button
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition-colors relative"
                aria-label="Notificaciones"
              >
                <Icon name="lucide:bell" class="w-5 h-5" />
                <span
                  v-if="unreadCount > 0"
                  class="absolute -top-0.5 -right-0.5 w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center"
                >
                  {{ unreadCount > 9 ? '9+' : unreadCount }}
                </span>
              </button>
            </div>
            <div v-if="isVendor" class="w-9 h-9 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
              {{ userInitials }}
            </div>
          </div>
        </div>
        <UiBreadcrumbs :items="breadcrumbs" />
      </header>
      <div id="main-content" class="flex-1 overflow-y-auto p-4 sm:p-8">
        <div v-if="isAdmin" class="overflow-x-auto">
          <slot />
        </div>
        <slot v-else />
      </div>
    </main>
  </div>
  <UiToast />
</template>

<script setup lang="ts">
const props = defineProps<{
  role: 'admin' | 'vendor'
}>()

const route = useRoute()
const auth = useAuthStore()
const router = useRouter()

const mobileOpen = ref(false)
const searchQuery = ref('')
const unreadCount = ref(0)
const notifRef = ref<HTMLElement | null>(null)

const user = computed(() => auth.user)
const userInitials = computed(() => {
  if (!user.value?.full_name) return '?'
  return user.value.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

const formattedDate = computed(() => {
  return new Date().toLocaleDateString('es-CR', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  })
})

const isAdmin = computed(() => props.role === 'admin')
const isVendor = computed(() => props.role === 'vendor')

const isVendorPage = computed(() => {
  if (!isVendor.value) return true
  return !['/vendor/login', '/vendor/register'].includes(route.path)
})

const showSidebar = computed(() => isAdmin.value || isVendorPage.value)
const showHeader = computed(() => isAdmin.value || isVendorPage.value)

const mainMarginClass = computed(() => showSidebar.value ? 'lg:ml-64' : '')

// Theme classes
const sidebarTheme = computed(() =>
  isAdmin.value
    ? 'bg-white border-r border-gray-200 text-gray-900'
    : 'bg-slate-900 text-white'
)

const sidebarBorderClass = computed(() =>
  isAdmin.value ? 'border-b border-gray-100' : 'border-b border-slate-800'
)

const logoTitleClass = computed(() =>
  isAdmin.value ? 'font-bold text-gray-900 text-sm' : 'font-bold text-white text-sm'
)

const logoSubtitleClass = computed(() =>
  isAdmin.value ? 'text-xs text-primary-500 font-semibold' : 'text-xs text-primary-400'
)

const logoTitle = computed(() => isAdmin.value ? 'Costa Rica' : 'Vendor Panel')
const logoSubtitle = computed(() => isAdmin.value ? 'Travel Admin' : 'Costa Rica Travel')

const navGroupLabelClass = computed(() =>
  isAdmin.value ? 'text-gray-400' : 'text-slate-500'
)

const navLinkClass = (path: string, exact: boolean) => {
  const isActive = exact ? route.path === path : route.path.startsWith(path)
  if (isAdmin.value) {
    return isActive
      ? 'bg-primary-50 text-primary-600 border-primary-500'
      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 border-transparent'
  }
  return isActive
    ? 'bg-gradient-to-r from-primary-500/20 to-primary-600/10 text-primary-400 border-primary-500'
    : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 border-transparent'
}

const userSectionBgClass = computed(() =>
  isAdmin.value ? 'p-2 bg-gray-50 rounded-xl' : ''
)

const avatarClass = computed(() =>
  isAdmin.value
    ? 'w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center text-white font-bold text-sm'
    : 'w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold text-sm'
)

const userNameClass = computed(() =>
  isAdmin.value ? 'font-medium text-gray-900 text-sm truncate' : 'text-sm font-medium text-white truncate'
)

const userDetailClass = computed(() =>
  isAdmin.value ? 'text-xs text-gray-500 capitalize truncate' : 'text-xs text-slate-400 truncate'
)

const userDetail = computed(() =>
  isAdmin.value ? (user.value?.role?.replace('_', ' ') || '') : (user.value?.email || '')
)

const logoutClass = computed(() =>
  isAdmin.value
    ? 'text-gray-500 hover:text-red-600 hover:bg-red-50'
    : 'text-slate-400 hover:text-red-400 hover:bg-red-500/10'
)

// Page title
const adminTitles: Record<string, string> = {
  '/admin/dashboard': 'Dashboard',
  '/admin/users': 'Usuarios',
  '/admin/vendors': 'Proveedores',
  '/admin/bookings': 'Reservas',
  '/admin/blog': 'Blog',
  '/admin/blog/new': 'Nuevo Artículo',
  '/admin/destinations': 'Destinos',
  '/admin/reports': 'Reportes',
  '/admin/settings': 'Configuración'
}

const vendorTitles: Record<string, string> = {
  '/vendor/dashboard': 'Dashboard',
  '/vendor/analytics': 'Estadísticas',
  '/vendor/properties': 'Propiedades',
  '/vendor/properties/new': 'Nueva Propiedad',
  '/vendor/tours': 'Tours',
  '/vendor/tours/new': 'Nuevo Tour',
  '/vendor/bookings': 'Reservas',
  '/vendor/payouts': 'Pagos',
  '/vendor/marketing': 'Marketing',
  '/vendor/settings': 'Configuración'
}

const pageTitle = computed(() => {
  const titles = isAdmin.value ? adminTitles : vendorTitles
  const path = route.path
  if (isVendor.value) {
    if (path.startsWith('/vendor/properties/') && !path.endsWith('/new')) return 'Editar Propiedad'
    if (path.startsWith('/vendor/tours/') && !path.endsWith('/new')) return 'Editar Tour'
  }
  return titles[path] || (isAdmin.value ? 'Admin' : 'Vendor')
})

// Menu items
const mainMenuItems = computed(() =>
  isAdmin.value
    ? [
        { icon: 'lucide:layout-dashboard', label: 'Dashboard', path: '/admin/dashboard' },
        { icon: 'lucide:users', label: 'Usuarios', path: '/admin/users' },
        { icon: 'lucide:store', label: 'Proveedores', path: '/admin/vendors' },
      ]
    : [
        { icon: 'lucide:layout-dashboard', label: 'Dashboard', path: '/vendor/dashboard' },
        { icon: 'lucide:bar-chart-3', label: 'Estadísticas', path: '/vendor/analytics' },
      ]
)

const managementMenuItems = computed(() =>
  isAdmin.value
    ? [
        { icon: 'lucide:calendar-check', label: 'Reservas', path: '/admin/bookings' },
        { icon: 'lucide:newspaper', label: 'Blog', path: '/admin/blog' },
        { icon: 'lucide:map-pin', label: 'Destinos', path: '/admin/destinations' },
        { icon: 'lucide:settings', label: 'Configuración', path: '/admin/settings' },
      ]
    : [
        { icon: 'lucide:building-2', label: 'Propiedades', path: '/vendor/properties' },
        { icon: 'lucide:mountain', label: 'Tours', path: '/vendor/tours' },
        { icon: 'lucide:calendar-check', label: 'Reservas', path: '/vendor/bookings' },
        { icon: 'lucide:credit-card', label: 'Pagos', path: '/vendor/payouts' },
        { icon: 'lucide:megaphone', label: 'Marketing', path: '/vendor/marketing' },
        { icon: 'lucide:settings', label: 'Configuración', path: '/vendor/settings' },
      ]
)

// Breadcrumbs
const breadcrumbs = computed(() => {
  const crumbs: { label: string; to?: string }[] = []
  if (isAdmin.value || isVendorPage.value) {
    const prefix = isAdmin.value ? 'Admin' : 'Panel'
    const dashboard = isAdmin.value ? '/admin/dashboard' : '/vendor/dashboard'
    crumbs.push({ label: prefix, to: dashboard })
    const segments = route.path.split('/').filter(Boolean)
    if (segments.length > 1) {
      const sub = segments.slice(1).join('/')
      if (sub !== 'dashboard') {
        crumbs.push({ label: pageTitle.value })
      }
    }
  }
  return crumbs
})

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push(`/admin/users?q=${encodeURIComponent(searchQuery.value.trim())}`)
  }
}

const logout = () => {
  auth.logout()
  router.push(isAdmin.value ? '/login' : '/vendor/login')
}

watch(() => route.path, () => {
  mobileOpen.value = false
})
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

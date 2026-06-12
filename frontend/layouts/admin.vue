<template>
  <div class="flex min-h-screen bg-gray-50">
    <a href="#main-content" class="skip-link">Ir al contenido principal</a>

    <Transition name="fade">
      <div v-if="mobileOpen" class="fixed inset-0 bg-black/50 z-30 lg:hidden" @click="mobileOpen = false" />
    </Transition>

    <aside
      class="w-64 bg-white border-r border-gray-200 flex flex-col fixed h-full z-40 transition-transform duration-300 lg:translate-x-0"
      :class="mobileOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div class="p-4 border-b border-gray-100">
        <NuxtLink to="/" class="flex items-center gap-3 hover:opacity-90 transition-opacity">
          <div class="w-9 h-9 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
            <Icon name="lucide:tree-palm" class="w-5 h-5 text-white" />
          </div>
          <div>
            <span class="font-bold text-gray-900 text-sm">Costa Rica</span>
            <p class="text-xs text-primary-500 font-semibold">Travel Admin</p>
          </div>
        </NuxtLink>
      </div>

      <nav class="flex-1 py-4 overflow-y-auto">
        <div class="mb-6">
          <p class="px-4 mb-2 text-[10px] font-bold text-gray-400 uppercase tracking-wider">Principal</p>
          <div class="mx-2 space-y-0.5">
            <NuxtLink
              v-for="item in mainMenuItems"
              :key="item.path"
              :to="item.path"
              class="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 text-sm font-medium group"
              :class="$route.path === item.path
                ? 'bg-primary-50 text-primary-600 border-l-2 border-primary-500'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 border-l-2 border-transparent'"
              :aria-current="$route.path === item.path ? 'page' : undefined"
              @click="mobileOpen = false"
            >
              <Icon :name="item.icon" class="w-5 h-5 flex-shrink-0" />
              <span class="flex-1">{{ item.label }}</span>
            </NuxtLink>
          </div>
        </div>

        <div class="mb-6">
          <p class="px-4 mb-2 text-[10px] font-bold text-gray-400 uppercase tracking-wider">Gestión</p>
          <div class="mx-2 space-y-0.5">
            <NuxtLink
              v-for="item in managementMenuItems"
              :key="item.path"
              :to="item.path"
              class="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 text-sm font-medium group"
              :class="$route.path.startsWith(item.path)
                ? 'bg-primary-50 text-primary-600 border-l-2 border-primary-500'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 border-l-2 border-transparent'"
              :aria-current="$route.path.startsWith(item.path) ? 'page' : undefined"
              @click="mobileOpen = false"
            >
              <Icon :name="item.icon" class="w-5 h-5 flex-shrink-0" />
              <span class="flex-1">{{ item.label }}</span>
            </NuxtLink>
          </div>
        </div>
      </nav>

      <div class="p-4 border-t border-gray-100">
        <div class="flex items-center gap-3 mb-3 p-2 bg-gray-50 rounded-xl">
          <div class="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
            {{ userInitials }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-gray-900 text-sm truncate">{{ user?.full_name || 'Usuario' }}</p>
            <p class="text-xs text-gray-500 capitalize truncate">{{ user?.role?.replace('_', ' ') }}</p>
          </div>
        </div>
        <button
          @click="logout"
          class="flex items-center gap-3 px-3 py-2 w-full text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors text-sm"
        >
          <Icon name="lucide:log-out" class="w-4 h-4" />
          <span>Cerrar sesión</span>
        </button>
      </div>
    </aside>

    <main class="flex-1 min-h-screen flex flex-col lg:ml-64">
      <header class="bg-white border-b border-gray-200 px-4 sm:px-8 py-4 sticky top-0 z-10">
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
              <p class="text-xs text-gray-500 mt-0.5 hidden sm:block">{{ currentDate }}</p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <div class="hidden md:block relative">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Buscar usuarios..."
                class="pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400 w-48 lg:w-64"
                @keyup.enter="handleSearch"
              >
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
          </div>
        </div>
        <UiBreadcrumbs :items="breadcrumbs" />
      </header>

      <div id="main-content" class="flex-1 overflow-y-auto p-4 sm:p-8">
        <div class="overflow-x-auto">
          <slot />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
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

const currentDate = computed(() => {
  return new Date().toLocaleDateString('es-CR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
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
  return titles[route.path] || 'Admin'
})

const breadcrumbs = computed(() => {
  const crumbs: { label: string; to?: string }[] = []
  const path = route.path
  if (path.startsWith('/admin')) {
    crumbs.push({ label: 'Admin', to: '/admin/dashboard' })
    const segments = path.split('/').filter(Boolean)
    if (segments.length > 1) {
      const sub = segments.slice(1).join('/')
      if (sub !== 'dashboard') {
        crumbs.push({ label: pageTitle.value })
      }
    }
  }
  return crumbs
})

const mainMenuItems = [
  { icon: 'lucide:layout-dashboard', label: 'Dashboard', path: '/admin/dashboard' },
  { icon: 'lucide:users', label: 'Usuarios', path: '/admin/users' },
  { icon: 'lucide:store', label: 'Proveedores', path: '/admin/vendors' },
]

const managementMenuItems = [
  { icon: 'lucide:calendar-check', label: 'Reservas', path: '/admin/bookings' },
  { icon: 'lucide:newspaper', label: 'Blog', path: '/admin/blog' },
  { icon: 'lucide:map-pin', label: 'Destinos', path: '/admin/destinations' },
  { icon: 'lucide:bar-chart-3', label: 'Reportes', path: '/admin/reports' },
  { icon: 'lucide:settings', label: 'Configuración', path: '/admin/settings' },
]

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push(`/admin/users?q=${encodeURIComponent(searchQuery.value.trim())}`)
  }
}

const logout = () => {
  auth.logout()
  router.push('/login')
}

onMounted(() => {
  auth.initAuth()
  if (!auth.isAuthenticated || !['super_admin', 'admin'].includes(auth.user?.role || '')) {
    router.push('/login')
  }
})

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

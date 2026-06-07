<template>
  <div class="flex min-h-screen bg-gray-50">
    <!-- Skip to main content -->
    <a href="#main-content" class="skip-link">Ir al contenido principal</a>

    <!-- Mobile sidebar overlay -->
    <Transition name="fade">
      <div v-if="mobileOpen" class="fixed inset-0 bg-black/50 z-30 lg:hidden" @click="mobileOpen = false" />
    </Transition>

    <!-- Sidebar - Modern Light -->
    <aside
      class="w-64 bg-white border-r border-gray-200 flex flex-col fixed h-full z-40 transition-transform duration-300 lg:translate-x-0"
      :class="mobileOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <!-- Logo -->
      <div class="p-5 border-b border-gray-100">
        <NuxtLink to="/" class="flex items-center gap-3">
          <div class="w-10 h-10 bg-gradient-to-br from-primary to-primary-light rounded-xl flex items-center justify-center">
            <span class="text-xl">🌴</span>
          </div>
          <div>
            <span class="font-bold text-gray-900 text-sm">Costa Rica</span>
            <p class="text-xs text-primary font-semibold">Travel Admin</p>
          </div>
        </NuxtLink>
      </div>
      
      <!-- Navigation -->
      <nav class="flex-1 p-4 space-y-1 overflow-y-auto">
          <NuxtLink 
            v-for="item in menuItems" 
            :key="item.path"
            :to="item.path"
            class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium"
            :class="$route.path === item.path 
              ? 'bg-primary/10 text-primary' 
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'"
            :aria-current="$route.path === item.path ? 'page' : undefined"
            @click="mobileOpen = false"
          >
          <span class="text-lg">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </NuxtLink>
      </nav>

      <!-- User Section -->
      <div class="p-4 border-t border-gray-100">
        <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
          <div class="w-10 h-10 bg-gradient-to-br from-primary to-primary-light rounded-full flex items-center justify-center text-white font-bold text-sm">
            {{ userInitials }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-gray-900 text-sm truncate">{{ user?.full_name }}</p>
            <p class="text-xs text-gray-500 capitalize">{{ user?.role?.replace('_', ' ') }}</p>
          </div>
        </div>
        <button @click="logout" class="mt-3 flex items-center gap-2 px-4 py-2 w-full text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors text-sm">
          <span>🚪</span>
          <span>Cerrar sesión</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col lg:ml-64">
      <!-- Header -->
      <header class="bg-white border-b border-gray-200 px-4 sm:px-8 py-4 sticky top-0 z-10">
        <div class="flex items-center justify-between">
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
              <h1 class="text-xl sm:text-2xl font-bold text-gray-900">{{ pageTitle }}</h1>
              <p class="text-gray-500 text-sm hidden sm:block">{{ currentDate }}</p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <!-- Search -->
            <div class="hidden md:block relative">
              <input type="text" placeholder="Buscar..." class="pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary w-48 lg:w-64">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
            </div>
            <!-- Notifications -->
            <button class="p-2.5 bg-gray-50 rounded-xl text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors relative">
              <span class="text-lg">🔔</span>
              <span class="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-white"></span>
            </button>
          </div>
        </div>
        <UiBreadcrumbs :items="breadcrumbs" />
      </header>

      <!-- Page Content -->
      <div id="main-content" class="flex-1 overflow-y-auto p-4 sm:p-8">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const auth = useAuthStore()
const router = useRouter()

const mobileOpen = ref(false)

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

const menuItems = [
  { icon: '📊', label: 'Dashboard', path: '/admin/dashboard' },
  { icon: '👥', label: 'Usuarios', path: '/admin/users' },
  { icon: '🏪', label: 'Proveedores', path: '/admin/vendors' },
  { icon: '📋', label: 'Reservas', path: '/admin/bookings' },
  { icon: '📝', label: 'Blog', path: '/admin/blog' },
  { icon: '🗺️', label: 'Destinos', path: '/admin/destinations' },
  { icon: '📈', label: 'Reportes', path: '/admin/reports' },
  { icon: '⚙️', label: 'Configuración', path: '/admin/settings' }
]

const logout = () => {
  auth.logout()
  router.push('/login')
}

watch(() => route.path, () => { mobileOpen.value = false })

onMounted(() => {
  auth.initAuth()
  if (!auth.isAuthenticated || !['super_admin', 'admin'].includes(auth.user?.role || '')) {
    router.push('/login')
  }
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
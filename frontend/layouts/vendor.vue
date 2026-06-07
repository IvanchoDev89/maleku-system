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
      v-if="isVendorPage"
      class="w-64 bg-slate-900 text-white flex flex-col fixed h-full z-40 transition-transform duration-300 lg:translate-x-0"
      :class="mobileOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <!-- Logo -->
      <div class="p-4 border-b border-slate-800">
        <NuxtLink to="/" class="flex items-center gap-3 hover:opacity-90 transition-opacity">
          <div class="w-9 h-9 bg-gradient-to-br from-teal-500 to-teal-600 rounded-lg flex items-center justify-center">
            <span class="text-xl">🌴</span>
          </div>
          <div>
            <span class="font-bold text-white text-sm">Vendor Panel</span>
            <p class="text-xs text-teal-400">Costa Rica Travel</p>
          </div>
        </NuxtLink>
      </div>
      
      <!-- Navigation -->
      <nav class="flex-1 py-4 overflow-y-auto">
        <div class="mb-6">
          <p class="px-4 mb-2 text-[10px] font-bold text-slate-500 uppercase tracking-wider">Principal</p>
          <div class="mx-2 space-y-0.5">
              <NuxtLink 
                v-for="item in mainMenuItems" 
                :key="item.path"
                :to="item.path"
                class="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 text-sm font-medium group"
                :class="$route.path === item.path 
                  ? 'bg-gradient-to-r from-teal-500/20 to-teal-600/10 text-teal-400 border-l-2 border-teal-500' 
                  : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 border-l-2 border-transparent'"
                :aria-current="$route.path === item.path ? 'page' : undefined"
                @click="mobileOpen = false"
              >
              <span class="text-lg">{{ item.icon }}</span>
              <span class="flex-1">{{ item.label }}</span>
            </NuxtLink>
          </div>
        </div>

        <div class="mb-6">
          <p class="px-4 mb-2 text-[10px] font-bold text-slate-500 uppercase tracking-wider">Gestión</p>
          <div class="mx-2 space-y-0.5">
              <NuxtLink 
                v-for="item in managementMenuItems" 
                :key="item.path"
                :to="item.path"
                class="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 text-sm font-medium group"
                :class="$route.path.startsWith(item.path)
                  ? 'bg-gradient-to-r from-teal-500/20 to-teal-600/10 text-teal-400 border-l-2 border-teal-500' 
                  : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 border-l-2 border-transparent'"
                :aria-current="$route.path.startsWith(item.path) ? 'page' : undefined"
                @click="mobileOpen = false"
              >
              <span class="text-lg">{{ item.icon }}</span>
              <span class="flex-1">{{ item.label }}</span>
            </NuxtLink>
          </div>
        </div>
      </nav>

      <!-- User Section -->
      <div class="p-4 border-t border-slate-800">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 bg-teal-600 rounded-full flex items-center justify-center text-white font-bold">
            {{ userInitials }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-white truncate">{{ user?.full_name || 'Usuario' }}</p>
            <p class="text-xs text-slate-400 truncate">{{ user?.email }}</p>
          </div>
        </div>
        <button 
          @click="logout" 
          class="flex items-center gap-3 px-3 py-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg w-full transition-colors text-sm"
        >
          <span>🚪</span>
          <span>Cerrar Sesión</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main
      class="flex-1 min-h-screen flex flex-col"
      :class="isVendorPage ? 'lg:ml-64' : ''"
    >
      <header v-if="isVendorPage" class="bg-white border-b border-gray-200 px-4 sm:px-8 py-4 sticky top-0 z-10">
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
          </div>
        </div>
        <UiBreadcrumbs :items="breadcrumbs" />
      </header>
      <div id="main-content" class="flex-1 p-4 sm:p-8">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const mobileOpen = ref(false)

const user = computed(() => auth.user)
const userInitials = computed(() => {
  const name = user.value?.full_name || 'U'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

const isVendorPage = computed(() => {
  return route.path.startsWith('/vendor/') && !['/vendor/login', '/vendor/register'].includes(route.path)
})

const pageTitle = computed(() => {
  const path = route.path
  const titles: Record<string, string> = {
    '/vendor/dashboard': 'Dashboard',
    '/vendor/analytics': 'Estadísticas',
    '/vendor/analytics/index': 'Estadísticas',
    '/vendor/properties': 'Propiedades',
    '/vendor/properties/new': 'Nueva Propiedad',
    '/vendor/tours': 'Tours',
    '/vendor/tours/new': 'Nuevo Tour',
    '/vendor/bookings': 'Reservas',
    '/vendor/payouts': 'Pagos',
    '/vendor/marketing': 'Marketing',
    '/vendor/settings': 'Configuración'
  }
  if (path.startsWith('/vendor/properties/') && !path.endsWith('/new')) {
    return 'Editar Propiedad'
  }
  if (path.startsWith('/vendor/tours/') && !path.endsWith('/new')) {
    return 'Editar Tour'
  }
  return titles[path] || 'Vendor'
})

const breadcrumbs = computed(() => {
  const crumbs: { label: string; to?: string }[] = []
  if (isVendorPage.value) {
    crumbs.push({ label: 'Panel', to: '/vendor/dashboard' })
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

const mainMenuItems = [
  { icon: '📊', label: 'Dashboard', path: '/vendor/dashboard' },
  { icon: '📈', label: 'Estadísticas', path: '/vendor/analytics' },
]

const managementMenuItems = [
  { icon: '🏨', label: 'Propiedades', path: '/vendor/properties' },
  { icon: '🧗', label: 'Tours', path: '/vendor/tours' },
  { icon: '📋', label: 'Reservas', path: '/vendor/bookings' },
  { icon: '💳', label: 'Pagos', path: '/vendor/payouts' },
  { icon: '📢', label: 'Marketing', path: '/vendor/marketing' },
  { icon: '⚙️', label: 'Configuración', path: '/vendor/settings' }
]

const logout = () => {
  auth.logout()
  router.push('/vendor/login')
}

watch(() => route.path, () => { mobileOpen.value = false })
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